from flask import Blueprint, render_template, request
from flask_login import login_required
from models import Video
from s3_service import generate_presigned_url, guess_content_type

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    featured = Video.query.filter_by(is_featured=True, is_published=True).limit(1).first()
    trending = Video.query.filter_by(is_published=True).order_by(Video.view_count.desc()).limit(12).all()
    recent = Video.query.filter_by(is_published=True).order_by(Video.created_at.desc()).limit(12).all()

    # Generate thumbnail URLs
    for v in [featured] + trending + recent:
        if v and v.s3_thumbnail_key:
            v.thumbnail_url = generate_presigned_url(
                v.s3_thumbnail_key,
                expiry=7200,
                response_content_type=guess_content_type(v.s3_thumbnail_key, 'image/jpeg')
            )
        elif v:
            v.thumbnail_url = None

    genres = db.session.query(Video.genre).filter(
        Video.genre.isnot(None), Video.is_published == True
    ).distinct().all()
    genres = [g[0] for g in genres if g[0]]

    return render_template('main/index.html',
                           featured=featured,
                           trending=trending,
                           recent=recent,
                           genres=genres)


@main_bp.route('/browse')
@login_required
def browse():
    genre = request.args.get('genre')
    search = request.args.get('q', '').strip()
    query = Video.query.filter_by(is_published=True)

    if genre:
        query = query.filter_by(genre=genre)
    if search:
        query = query.filter(Video.title.ilike(f'%{search}%'))

    videos = query.order_by(Video.created_at.desc()).all()
    for v in videos:
        if v.s3_thumbnail_key:
            v.thumbnail_url = generate_presigned_url(
                v.s3_thumbnail_key,
                expiry=7200,
                response_content_type=guess_content_type(v.s3_thumbnail_key, 'image/jpeg')
            )
        else:
            v.thumbnail_url = None

    genres = db.session.query(Video.genre).filter(
        Video.genre.isnot(None), Video.is_published == True
    ).distinct().all()
    genres = [g[0] for g in genres if g[0]]

    return render_template('main/browse.html', videos=videos, genres=genres,
                           selected_genre=genre, search=search)


# avoid circular import
from extensions import db
