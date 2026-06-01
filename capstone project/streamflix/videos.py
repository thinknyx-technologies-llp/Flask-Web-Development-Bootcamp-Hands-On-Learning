from flask import Blueprint, Response, abort, jsonify, render_template, request, stream_with_context, url_for
from flask_login import login_required
from models import Video
from extensions import db
from s3_service import generate_presigned_url, get_s3_object, guess_content_type, head_s3_object

videos_bp = Blueprint('videos', __name__, url_prefix='/watch')


@videos_bp.route('/<int:video_id>')
@login_required
def watch(video_id):
    video = Video.query.get_or_404(video_id)
    if not video.is_published:
        abort(404)

    # Increment view count
    video.view_count += 1
    db.session.commit()

    video_content_type = guess_content_type(video.s3_video_key, 'video/mp4')
    stream_url = url_for('videos.stream_video', video_id=video.id)
    direct_stream_url = generate_presigned_url(
        video.s3_video_key,
        response_content_type=video_content_type
    )

    thumbnail_url = None
    if video.s3_thumbnail_key:
        thumbnail_url = generate_presigned_url(
            video.s3_thumbnail_key,
            expiry=7200,
            response_content_type=guess_content_type(video.s3_thumbnail_key, 'image/jpeg')
        )

    # Suggest related videos (same genre)
    related = Video.query.filter(
        Video.genre == video.genre,
        Video.id != video.id,
        Video.is_published == True
    ).limit(8).all()

    for v in related:
        if v.s3_thumbnail_key:
            v.thumbnail_url = generate_presigned_url(
                v.s3_thumbnail_key,
                expiry=7200,
                response_content_type=guess_content_type(v.s3_thumbnail_key, 'image/jpeg')
            )
        else:
            v.thumbnail_url = None

    return render_template('videos/watch.html',
                           video=video,
                           stream_url=stream_url,
                           direct_stream_url=direct_stream_url,
                           video_content_type=video_content_type,
                           thumbnail_url=thumbnail_url,
                           related=related)


@videos_bp.route('/<int:video_id>/stream', methods=['GET', 'HEAD'])
@login_required
def stream_video(video_id):
    """Stream a private S3 video through Flask with browser-friendly range support."""
    video = Video.query.get_or_404(video_id)
    if not video.is_published:
        abort(404)

    try:
        metadata = head_s3_object(video.s3_video_key)
    except Exception as e:
        return Response(str(e), status=502, mimetype='text/plain')

    total_size = metadata['ContentLength']
    content_type = metadata.get('ContentType')
    guessed_content_type = guess_content_type(video.s3_video_key, 'video/mp4')
    if not content_type or not content_type.startswith(('video/', 'audio/')):
        content_type = guessed_content_type

    range_header = request.headers.get('Range')
    status = 200
    headers = {
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'no-store, no-transform',
        'Content-Type': content_type,
        'X-Content-Type-Options': 'nosniff',
    }

    byte_range = None
    start = 0
    end = total_size - 1

    if range_header:
        try:
            units, requested_range = range_header.split('=', 1)
            if units.strip().lower() != 'bytes':
                abort(416)

            start_text, end_text = requested_range.split('-', 1)
            start_text = start_text.strip()
            end_text = end_text.strip()

            if start_text:
                start = int(start_text)
                if end_text:
                    end = int(end_text)
            elif end_text:
                suffix_length = int(end_text)
                if suffix_length <= 0:
                    abort(416)
                start = max(total_size - suffix_length, 0)
            else:
                abort(416)

            if start_text and end_text:
                end = int(end_text)

            if start < 0 or end >= total_size or start > end:
                abort(416)

            byte_range = f'bytes={start}-{end}'
            status = 206
            headers['Content-Range'] = f'bytes {start}-{end}/{total_size}'
        except ValueError:
            abort(416)
    else:
        end = min(total_size - 1, 1024 * 1024 - 1)
        byte_range = f'bytes={start}-{end}'
        status = 206
        headers['Content-Range'] = f'bytes {start}-{end}/{total_size}'

    content_length = end - start + 1
    headers['Content-Length'] = str(content_length)

    if request.method == 'HEAD':
        return Response(status=status, headers=headers)

    try:
        s3_object = get_s3_object(video.s3_video_key, byte_range=byte_range)
    except Exception as e:
        return Response(str(e), status=502, mimetype='text/plain')

    body = s3_object['Body']

    def generate():
        try:
            while True:
                chunk = body.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk
        finally:
            body.close()

    return Response(stream_with_context(generate()), status=status, headers=headers)


@videos_bp.route('/<int:video_id>/debug')
@login_required
def debug_video(video_id):
    """Return stream diagnostics for troubleshooting browser playback."""
    video = Video.query.get_or_404(video_id)
    if not video.is_published:
        abort(404)

    try:
        metadata = head_s3_object(video.s3_video_key)
        first_byte = get_s3_object(video.s3_video_key, byte_range='bytes=0-0')
        first_byte['Body'].close()
    except Exception as e:
        return jsonify({
            'ok': False,
            'error': str(e),
            's3_video_key': video.s3_video_key,
        }), 502

    return jsonify({
        'ok': True,
        'stream_url': url_for('videos.stream_video', video_id=video.id),
        's3_video_key': video.s3_video_key,
        's3_content_type': metadata.get('ContentType'),
        'browser_content_type': guess_content_type(video.s3_video_key, 'video/mp4'),
        'content_length': metadata.get('ContentLength'),
        'accept_ranges_supported': True,
        'note': 'If this is ok but the player fails, the file codec is probably not browser-supported. Use MP4 with H.264 video and AAC audio.',
    })
