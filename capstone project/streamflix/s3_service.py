import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError, NoCredentialsError
from flask import current_app
import uuid
import os
import mimetypes


def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION'],
        config=BotoConfig(signature_version='s3v4'),
    )


def get_bucket_name():
    bucket = (current_app.config.get('S3_BUCKET_NAME') or '').strip()
    if not bucket:
        raise Exception("S3_BUCKET_NAME is not set in your .env file")
    return bucket


def guess_content_type(filename, fallback='application/octet-stream'):
    content_type, _ = mimetypes.guess_type(filename or '')
    return content_type or fallback


def normalize_content_type(content_type, filename, fallback='application/octet-stream'):
    if content_type and content_type != 'application/octet-stream':
        return content_type
    return guess_content_type(filename, fallback)


def upload_file_to_s3(file_obj, folder='videos', filename=None, content_type=None):
    """
    Upload a file object to S3.
    Returns the S3 key on success, or raises an exception.
    """
    if file_obj is None:
        raise Exception("No file provided (file_obj is None)")

    s3 = get_s3_client()
    bucket = get_bucket_name()

    if not filename:
        ext = ''
        original = getattr(file_obj, 'filename', None) or ''
        if '.' in original:
            ext = '.' + original.rsplit('.', 1)[1].lower()
        filename = str(uuid.uuid4()) + ext

    s3_key = f"{folder}/{filename}"
    content_type = normalize_content_type(content_type, filename)

    extra_args = {}
    if content_type:
        extra_args['ContentType'] = content_type

    # Ensure we're at the start of the file stream
    if hasattr(file_obj, 'seek'):
        file_obj.seek(0)

    try:
        s3.upload_fileobj(file_obj, bucket, s3_key, ExtraArgs=extra_args)
        return s3_key
    except (ClientError, NoCredentialsError) as e:
        raise Exception(f"S3 upload failed: {str(e)}")


def generate_presigned_url(s3_key, expiry=None, response_content_type=None):
    """
    Generate a presigned URL for streaming/downloading a video.
    """
    s3 = get_s3_client()
    bucket = get_bucket_name()
    if expiry is None:
        expiry = current_app.config['S3_PRESIGNED_URL_EXPIRY']

    try:
        params = {'Bucket': bucket, 'Key': s3_key}
        if response_content_type:
            params['ResponseContentType'] = response_content_type

        url = s3.generate_presigned_url(
            'get_object',
            Params=params,
            ExpiresIn=expiry
        )
        return url
    except ClientError as e:
        raise Exception(f"Could not generate presigned URL: {str(e)}")


def head_s3_object(s3_key):
    """Fetch S3 object metadata without downloading the object."""
    s3 = get_s3_client()
    bucket = get_bucket_name()
    try:
        return s3.head_object(Bucket=bucket, Key=s3_key)
    except ClientError as e:
        raise Exception(f"Could not read S3 object metadata: {str(e)}")


def get_s3_object(s3_key, byte_range=None):
    """Fetch an S3 object, optionally using an HTTP byte range."""
    s3 = get_s3_client()
    bucket = get_bucket_name()
    params = {'Bucket': bucket, 'Key': s3_key}
    if byte_range:
        params['Range'] = byte_range

    try:
        return s3.get_object(**params)
    except ClientError as e:
        raise Exception(f"Could not read S3 object: {str(e)}")


def delete_file_from_s3(s3_key):
    """Delete a file from S3 by key."""
    s3 = get_s3_client()
    bucket = get_bucket_name()
    try:
        s3.delete_object(Bucket=bucket, Key=s3_key)
        return True
    except ClientError as e:
        raise Exception(f"S3 delete failed: {str(e)}")


def list_bucket_files(prefix=''):
    """List all files in the bucket under a given prefix."""
    s3 = get_s3_client()
    bucket = get_bucket_name()
    try:
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        return response.get('Contents', [])
    except ClientError as e:
        raise Exception(f"Could not list bucket: {str(e)}")
