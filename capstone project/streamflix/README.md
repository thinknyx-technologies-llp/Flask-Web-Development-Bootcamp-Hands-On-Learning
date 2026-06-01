# 🎬 StreamFlix — Netflix-style Streaming Platform

A full-stack streaming platform built with Flask + AWS S3.

## Features
- User authentication (signup / login / logout)
- Video streaming via S3 presigned URLs (no public bucket needed)
- Admin dashboard: upload, edit, delete, publish/unpublish videos
- User management (promote to admin)
- Browse by genre, search by title
- Responsive dark UI

---

## Project Structure

```
streamflix/
├── app.py              # App factory & entry point
├── config.py           # Config from environment variables
├── extensions.py       # SQLAlchemy + LoginManager instances
├── models.py           # User + Video DB models
├── auth.py             # /login, /signup, /logout routes
├── main.py             # / (home) and /browse routes
├── videos.py           # /watch/<id> streaming route
├── admin.py            # /admin/* routes (protected)
├── s3_service.py       # S3 upload / presigned URL / delete helpers
├── seed.py             # Creates first admin user
├── requirements.txt
├── .env.example        # Copy to .env and fill in values
└── templates/
    ├── base.html
    ├── auth/           login.html, signup.html
    ├── main/           index.html, browse.html
    ├── videos/         watch.html
    └── admin/          dashboard.html, videos.html, video_form.html, users.html
```

---

## Setup

### 1. Clone & install dependencies

```bash
cd streamflix
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your values
```

Required variables:
| Variable | Description |
|---|---|
| `SECRET_KEY` | Random secret for sessions |
| `AWS_ACCESS_KEY_ID` | Your AWS key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret |
| `AWS_REGION` | e.g. `us-east-1` |
| `S3_BUCKET_NAME` | Your S3 bucket name |
| `DATABASE_URL` | SQLite (default) or PostgreSQL URL |

### 3. AWS S3 Bucket Setup

1. Create an S3 bucket in the AWS Console.
2. **Block all public access** — videos are served via presigned URLs, so the bucket stays private.
3. Create an IAM user with these permissions:
   - `s3:PutObject`
   - `s3:GetObject`
   - `s3:DeleteObject`
   - `s3:ListBucket`
4. Attach the policy to the IAM user and generate Access Keys.
5. Add a **CORS policy** to the bucket (for in-browser video playback):

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": [
      "Accept-Ranges",
      "Content-Length",
      "Content-Range",
      "Content-Type"
    ],
    "MaxAgeSeconds": 3600
  }
]
```

### 4. Create the database & first admin

```bash
python seed.py
```

This creates `admin@streamflix.com` / `admin123` — **change the password immediately**.

### 5. Run

```bash
python app.py
```

Visit `http://localhost:5000`

---

## How Streaming Works

1. Videos are uploaded directly to your private S3 bucket.
2. When a user clicks Play, Flask generates a **presigned URL** (valid for 1 hour).
3. The browser's native `<video>` player streams directly from S3 — no proxying through Flask.
4. The player automatically refreshes the URL at the 55-minute mark.

This means:
- **Zero bandwidth cost on your server** for video delivery
- **Secure** — URLs expire and are tied to specific objects

---

## Production Tips

- Use **PostgreSQL** instead of SQLite (`DATABASE_URL=postgresql://...`)
- Put Flask behind **gunicorn** + **nginx**
- Set `DEBUG=False` and use a strong `SECRET_KEY`
- Consider **CloudFront** in front of S3 for lower latency globally
