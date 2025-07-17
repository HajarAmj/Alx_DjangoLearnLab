# LibraryProject

A Django-based library management system for learning Django development.

## Project Overview

This project serves as the foundation for developing Django applications, focusing on library management functionality.

## Setup Instructions

### Prerequisites
- Python 3.x installed on your system
- Django installed (`pip install django`)

### Installation

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd LibraryProject
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

4. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

6. Open your web browser and visit: `http://127.0.0.1:8000/`

## Project Structure

```
LibraryProject/
├── LibraryProject/
│   ├── __init__.py
│   ├── settings.py      # Django project configuration
│   ├── urls.py          # URL declarations and routing
│   ├── wsgi.py          # WSGI configuration for deployment
│   └── asgi.py          # ASGI configuration for async support
├── manage.py            # Command-line utility for Django project
└── README.md           # This file
```

## Key Files

- **`settings.py`**: Contains all configuration for the Django project including database settings, installed apps, middleware, and more.
- **`urls.py`**: The URL dispatcher that maps URL patterns to views.
- **`manage.py`**: Command-line utility that provides various Django management commands.

## Common Commands

- `python manage.py runserver` - Start the development server
- `python manage.py migrate` - Apply database migrations
- `python manage.py makemigrations` - Create new database migrations
- `python manage.py createsuperuser` - Create an admin user
- `python manage.py startapp <app_name>` - Create a new Django app

## Development

This project is set up for learning Django development. You can start by creating new apps and building library management features.

## License

This project is for educational purposes.
