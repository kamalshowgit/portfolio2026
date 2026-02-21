# Personal Portfolio (Django)

Production-ready Django portfolio with:
- Public profile/CV page
- Private edit area (session login)
- Calendar todo widget
- Contact form with DB + email delivery

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set env vars from `.env.example` as needed, then:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

## Production Checklist

1. Set these required env vars:
- `DEBUG=false`
- `SECRET_KEY=<strong-secret>`
- `ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`
- `PERSONAL_EDIT_USERNAME` and `PERSONAL_EDIT_PASSWORD`

2. Recommended env vars:
- `CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`
- `DATABASE_URL=postgres://...`
- SMTP vars (`EMAIL_*`, `CONTACT_RECEIVER_EMAIL`)

3. Run migrations and collect static:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

4. Run app server:

```bash
gunicorn siteproject.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
```

Or use:

```bash
Procfile
```

## Security Notes

- `DEBUG=false` enables secure defaults in `settings.py`
- HTTPS/cookie/HSTS settings are env-configurable
- Edit login credentials are no longer hardcoded; use env vars

## Static/Media

- Static: served by WhiteNoise from `STATIC_ROOT`
- Media: user uploads should be served by your reverse proxy/object storage in production
