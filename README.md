# FastAPI Blog

A full-stack blog built with **FastAPI**, **PostgreSQL** and server-rendered **Jinja2** templates. Users can register, log in, write posts, comment, upload profile pictures and reset forgotten passwords by email. The app is containerised with **Docker** and deployed on **Render**, with the database hosted on **Neon**.

**Live demo:** https://fastapi-blog-hxw2.onrender.com/

> The demo runs on free tiers, so the first request after a quiet period can take up to a minute while the server and database wake up. Password-reset emails may not be delivered on the live demo (see [Deployment notes](#deployment-notes)).

## Screenshots

| Home | Post with comments |
|---|---|
| ![Home page](docs/screenshots/home.png) | ![Post page](docs/screenshots/post.png) |

| Account page | Login |
|---|---|
| ![Account page](docs/screenshots/account.png) | ![Login page](docs/screenshots/login.png) |

## Features

- **Authentication:** registration and login with JWT access tokens
- **Password reset by email:** a time-limited reset link, sent as a background task so the request returns immediately
- **Posts:** create, read, update and delete, with pagination and per-user post pages
- **Comments:** comment on any post. A comment can be deleted by its author or by the post's owner
- **Dynamic sidebar:** latest posts, latest comments and top authors, loaded from a small API endpoint
- **Profile pictures:** upload, crop and store in S3-compatible object storage
- **Account management:** update your profile, change your password, delete your account
- **Dark and light themes**, plus an error page for 404 and 500 responses
- **Database migrations** with Alembic

## Tech stack

| Area | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL (Neon), Alembic migrations |
| Auth and security | JWT (PyJWT), Argon2 password hashing (pwdlib), security headers |
| Storage | S3-compatible object storage via boto3 |
| Email | SMTP via aiosmtplib |
| Frontend | Jinja2 templates, Bootstrap 5, vanilla JavaScript |
| Packaging and hosting | Docker, GitHub, Render |

## Project structure

```text
.
├── main.py              # App setup, page routes, error handlers
├── config.py            # Settings loaded from environment variables
├── database.py          # Async engine and session dependency
├── models.py            # SQLAlchemy models (User, Post, Comment, PasswordResetToken)
├── schemas.py           # Pydantic request/response models
├── auth.py              # Password hashing, JWT, reset tokens
├── email_utils.py       # Sending password-reset emails
├── image_utils.py       # Image processing and S3 uploads
├── routers/
│   ├── users.py         # /api/users
│   ├── posts.py         # /api/posts
│   ├── comments.py      # /api/posts/{id}/comments
│   └── sidebar.py       # /api/sidebar
├── templates/           # Jinja2 templates (including the email template)
├── static/              # CSS, JavaScript, icons
├── alembic/             # Database migrations
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Getting started

### Prerequisites

- Python 3.12 or newer
- A PostgreSQL database (local, or a free hosted one such as Neon)
- An S3-compatible bucket for profile pictures (optional, only needed for uploads)

### Run locally

```bash
git clone https://github.com/HimanshuSharmaaaa/fastapi-blog
cd https://github.com/HimanshuSharmaaaa/fastapi-blog

python -m venv .venv
# Windows:      .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

pip install -r requirements.txt

# Windows: copy .env.example .env      macOS/Linux: cp .env.example .env
# Then fill in the values (see the table below)

alembic upgrade head
fastapi dev main.py
```

Open http://localhost:8000. The interactive API docs are at http://localhost:8000/docs.

### Run with Docker

```bash
docker build -t fastapi-blog .
docker run --rm -p 8080:8080 --env-file .env fastapi-blog
```

Open http://localhost:8080. Inside a container, `localhost` refers to the container itself, so use a hosted database URL (or `host.docker.internal` for a database on your own machine).

## Environment variables

Create a `.env` file from `.env.example`. **Never commit it.**

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL URL, for example `postgresql+psycopg://USER:PASSWORD@HOST/DBNAME?sslmode=require` |
| `SECRET_KEY` | Secret used to sign JWTs. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `S3_BUCKET_NAME` | Bucket for profile pictures |
| `S3_REGION` | Bucket region, for example `us-east-1` |
| `S3_ACCESS_KEY_ID` | Access key for the bucket |
| `S3_SECRET_ACCESS_KEY` | Secret key for the bucket |
| `S3_ENDPOINT_URL` | Optional. Only for S3-compatible services other than AWS |
| `MAIL_SERVER`, `MAIL_PORT` | SMTP server and port |
| `MAIL_USERNAME`, `MAIL_PASSWORD` | SMTP credentials |
| `MAIL_FROM` | Sender address |
| `MAIL_USE_TLS` | `true` to use STARTTLS |
| `FRONTEND_URL` | Public URL of the site, used to build password-reset links |

## API overview

Full interactive documentation is available at `/docs` when the app is running.

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/api/users` | Register | No |
| POST | `/api/users/token` | Log in (returns a JWT) | No |
| GET | `/api/users/me` | Current user | Yes |
| PATCH | `/api/users/me/password` | Change password | Yes |
| POST | `/api/users/forgot-password` | Request a reset email | No |
| POST | `/api/users/reset-password` | Set a new password with a reset token | No |
| GET | `/api/users/{id}` | Public profile | No |
| GET | `/api/users/{id}/posts` | A user's posts (paginated) | No |
| PATCH | `/api/users/{id}` | Update your profile | Yes |
| DELETE | `/api/users/{id}` | Delete your account | Yes |
| PATCH / DELETE | `/api/users/{id}/picture` | Upload or remove a profile picture | Yes |
| GET | `/api/posts` | List posts (paginated) | No |
| POST | `/api/posts` | Create a post | Yes |
| GET | `/api/posts/{id}` | Get one post | No |
| PUT / PATCH | `/api/posts/{id}` | Update a post | Yes (owner) |
| DELETE | `/api/posts/{id}` | Delete a post | Yes (owner) |
| GET | `/api/posts/{id}/comments` | List comments | No |
| POST | `/api/posts/{id}/comments` | Add a comment | Yes |
| DELETE | `/api/posts/{id}/comments/{comment_id}` | Delete a comment | Yes (author or post owner) |
| GET | `/api/sidebar` | Latest posts, comments and top authors | No |

## Security notes

- Passwords are hashed with **Argon2** and never stored or returned in plain text.
- Password-reset tokens are stored hashed and expire after a set time.
- The forgot-password endpoint gives the same response whether or not the email exists, so it can't be used to discover accounts.
- User-written content is escaped by Jinja2 and rendered with `textContent` in the sidebar script to prevent XSS.
- Responses include security headers such as `X-Frame-Options` and `X-Content-Type-Options`.
- Secrets are read from environment variables and are excluded from git and from the Docker image.

## Deployment notes

- **Hosting:** Docker image deployed as a Render web service, with auto-deploy from the `main` branch.
- **Database:** Neon (serverless PostgreSQL). Migrations are applied with `alembic upgrade head` before deploying schema changes.
- **Cold starts:** free tiers sleep when idle, so the first request after a quiet period is slow.
- **Email:** free Render web services block outbound SMTP on ports 25, 465 and 587, so password-reset emails may not be sent on the free tier. Using a provider that offers port 2525 or an HTTP API, or a paid instance, resolves this.

## Credits

This project was built while following Corey Schafer's FastAPI tutorial series. The comments feature, the dynamic sidebar, the Docker image and the Render and Neon deployment were added or set up by me on top of that base.

## Author

**Himanshu Sharma**

- GitHub: https://github.com/HimanshuSharmaaaa/
- LinkedIn: https://www.linkedin.com/in/himanshu-sharma-4a7661328/


