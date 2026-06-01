import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///streamflix.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS S3
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    S3_BUCKET_NAME = (os.environ.get('S3_BUCKET_NAME') or '').strip()

    # Max upload size: 2 GB
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024

    # Presigned URL expiry in seconds (1 hour)
    S3_PRESIGNED_URL_EXPIRY = 3600
