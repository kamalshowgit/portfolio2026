Personal Django site scaffold

This workspace contains a minimal Django project (`siteproject`) and a `personal` app that provides:

- A public CV-like page at `/` showing profile, links, projects, and notes.
- An edit interface at `/edit/` protected by a dummy login (`admin` / `changeme`) where you can edit profile, add/remove links, projects, and notes.

Quick setup (on PythonAnywhere or your environment):

1. Create a virtualenv and activate it.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run migrations and create a superuser (optional):

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

3. Run the development server locally:

```bash
python manage.py runserver
```

4. On PythonAnywhere: create a web app, point WSGI to `siteproject.wsgi.application`, upload static/media, and set virtualenv. Collect static files:

```bash
python manage.py collectstatic
```

Notes:
- Dummy credentials for the edit interface are `admin` / `changeme`. Change them in `personal/views.py`.
- Adjust `siteproject/settings.py` for production (SECRET_KEY, DEBUG=False, ALLOWED_HOSTS).
