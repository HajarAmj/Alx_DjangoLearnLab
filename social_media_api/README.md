# Social Media API (Django + DRF + Token Auth)

A starter API built with Django and Django REST Framework.

## Features
- Custom `User` model extending `AbstractUser` with `bio`, `profile_picture`, and self-referential `followers` (non-symmetrical)
- Token authentication via `rest_framework.authtoken`
- Endpoints:
  - `POST /api/accounts/register/` — create a user and return auth token
  - `POST /api/accounts/login/` — login with username or email + password; returns auth token
  - `GET/PATCH /api/accounts/profile/` — get or update the authenticated user's profile

## Quickstart

### 1) Create & activate a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Initialize the project
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # optional
```

### 4) Run the dev server
```bash
python manage.py runserver
```

### 5) Test with curl or Postman

**Register:**
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/register/   -F "username=alice"   -F "email=alice@example.com"   -F "password=SuperSafePass123!"   -F "bio=hi there"   -F "profile_picture=@/path/to/avatar.png"
```

**Login (username):**
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/login/   -H "Content-Type: application/json"   -d '{"username":"alice","password":"SuperSafePass123!"}'
```

**Login (email):**
```bash
curl -X POST http://127.0.0.1:8000/api/accounts/login/   -H "Content-Type: application/json"   -d '{"email":"alice@example.com","password":"SuperSafePass123!"}'
```

**Get profile:**
```bash
curl http://127.0.0.1:8000/api/accounts/profile/   -H "Authorization: Token <YOUR_TOKEN>"
```

**Update profile:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/accounts/profile/   -H "Authorization: Token <YOUR_TOKEN>"   -H "Content-Type: application/json"   -d '{"bio":"new bio"}'
```

## Project Structure
```
social_media_api/
├── accounts/
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── media/  # uploaded profile pictures
├── social_media_api/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## Notes
- The API defaults to `TokenAuthentication` and `IsAuthenticated` globally; registration and login views explicitly allow anonymous access.
- Make sure to set a secure `DJANGO_SECRET_KEY` for production and configure proper `ALLOWED_HOSTS`.
- The `followers` field relates users in a non-symmetrical way: adding a follower to a user does not automatically add the reverse.
- For image uploads, this project uses Pillow; files are served from `/media/` in development.

## Next Steps
- Add endpoints to follow/unfollow users and list followers/following.
- Add pagination and filtering to future list endpoints.
- Switch to JWT if you prefer stateless tokens for larger deployments.
