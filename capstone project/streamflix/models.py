from extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Video(db.Model):
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    genre = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.String(10), nullable=True)  # e.g. PG, PG-13, R
    duration_minutes = db.Column(db.Integer, nullable=True)

    # S3 keys
    s3_video_key = db.Column(db.String(500), nullable=False)   # path in bucket
    s3_thumbnail_key = db.Column(db.String(500), nullable=True)

    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'year': self.year,
            'rating': self.rating,
            'duration_minutes': self.duration_minutes,
            'is_featured': self.is_featured,
            'is_published': self.is_published,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat(),
        }

    def __repr__(self):
        return f'<Video {self.title}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
