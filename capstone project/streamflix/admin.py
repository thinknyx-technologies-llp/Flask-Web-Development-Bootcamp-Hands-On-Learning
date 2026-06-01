from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import Video, User
from extensions import db
from s3_service import (
    upload_file_to_s3,
    delete_file_from_s3,
    generate_presigned_url,
    guess_content_type,
    normalize_content_type,
)
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/')
@admin_required
def dashboard():
    total_videos = Video.query.count()
    total_users = User.query.count()
    published = Video.query.filter_by(is_published=True).count()
    total_views = db.session.query(db.func.sum(Video.view_count)).scalar() or 0
    recent_videos = Video.query.order_by(Video.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_videos=total_videos,
                           total_users=total_users,
                           published=published,
                           total_views=total_views,
                           recent_videos=recent_videos,
                           recent_users=recent_users)


@admin_bp.route('/videos')
@admin_required
def videos():
    all_videos = Video.query.order_by(Video.created_at.desc()).all()
    for v in all_videos:
        if v.s3_thumbnail_key:
            v.thumbnail_url = generate_presigned_url(
                v.s3_thumbnail_key,
                expiry=3600,
                response_content_type=guess_content_type(v.s3_thumbnail_key, 'image/jpeg')
            )
        else:
            v.thumbnail_url = None
    return render_template('admin/videos.html', videos=all_videos)


@admin_bp.route('/videos/add', methods=['GET', 'POST'])
@admin_required
def add_video():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        genre = request.form.get('genre', '').strip()
        year = request.form.get('year')
        rating = request.form.get('rating', '').strip()
        duration = request.form.get('duration')
        is_featured = request.form.get('is_featured') == 'on'
        is_published = request.form.get('is_published') == 'on'

        if not title:
            flash('Title is required.', 'error')
            return render_template('admin/video_form.html', video=None)

        video_file = request.files.get('video_file')
        thumbnail_file = request.files.get('thumbnail_file')

        if not video_file or video_file.filename == '':
            flash('Video file is required.', 'error')
            return render_template('admin/video_form.html', video=None)

        try:
            video_ct = normalize_content_type(video_file.content_type, video_file.filename, 'video/mp4')
            s3_video_key = upload_file_to_s3(
                video_file, folder='videos',
                content_type=video_ct
            )
            s3_thumbnail_key = None
            if thumbnail_file and (thumbnail_file.filename or '') != '':
                thumb_ct = normalize_content_type(thumbnail_file.content_type, thumbnail_file.filename, 'image/jpeg')
                s3_thumbnail_key = upload_file_to_s3(
                    thumbnail_file, folder='thumbnails',
                    content_type=thumb_ct
                )
        except Exception as e:
            flash(f'Upload failed: {str(e)}', 'error')
            return render_template('admin/video_form.html', video=None)

        video = Video(
            title=title,
            description=description,
            genre=genre,
            year=int(year) if year else None,
            rating=rating,
            duration_minutes=int(duration) if duration else None,
            s3_video_key=s3_video_key,
            s3_thumbnail_key=s3_thumbnail_key,
            is_featured=is_featured,
            is_published=is_published,
        )
        db.session.add(video)
        db.session.commit()
        flash(f'"{title}" added successfully!', 'success')
        return redirect(url_for('admin.videos'))

    return render_template('admin/video_form.html', video=None)


@admin_bp.route('/videos/<int:video_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)

    if request.method == 'POST':
        video.title = request.form.get('title', '').strip()
        video.description = request.form.get('description', '').strip()
        video.genre = request.form.get('genre', '').strip()
        year = request.form.get('year')
        video.year = int(year) if year else None
        video.rating = request.form.get('rating', '').strip()
        duration = request.form.get('duration')
        video.duration_minutes = int(duration) if duration else None
        video.is_featured = request.form.get('is_featured') == 'on'
        video.is_published = request.form.get('is_published') == 'on'

        # Replace thumbnail if new one provided
        thumbnail_file = request.files.get('thumbnail_file')
        if thumbnail_file and thumbnail_file.filename != '':
            try:
                if video.s3_thumbnail_key:
                    delete_file_from_s3(video.s3_thumbnail_key)
                video.s3_thumbnail_key = upload_file_to_s3(
                    thumbnail_file, folder='thumbnails',
                    content_type=normalize_content_type(
                        thumbnail_file.content_type,
                        thumbnail_file.filename,
                        'image/jpeg'
                    )
                )
            except Exception as e:
                flash(f'Thumbnail upload failed: {str(e)}', 'error')

        db.session.commit()
        flash(f'"{video.title}" updated.', 'success')
        return redirect(url_for('admin.videos'))

    return render_template('admin/video_form.html', video=video)


@admin_bp.route('/videos/<int:video_id>/delete', methods=['POST'])
@admin_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    try:
        delete_file_from_s3(video.s3_video_key)
        if video.s3_thumbnail_key:
            delete_file_from_s3(video.s3_thumbnail_key)
    except Exception as e:
        flash(f'Warning: S3 delete failed: {str(e)}', 'warning')

    db.session.delete(video)
    db.session.commit()
    flash(f'"{video.title}" deleted.', 'success')
    return redirect(url_for('admin.videos'))


@admin_bp.route('/videos/<int:video_id>/toggle', methods=['POST'])
@admin_required
def toggle_published(video_id):
    video = Video.query.get_or_404(video_id)
    video.is_published = not video.is_published
    db.session.commit()
    status = 'published' if video.is_published else 'unpublished'
    flash(f'"{video.title}" {status}.', 'success')
    return redirect(url_for('admin.videos'))


@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't change your own admin status.", 'error')
        return redirect(url_for('admin.users'))
    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f'{user.username} admin status updated.', 'success')
    return redirect(url_for('admin.users'))
