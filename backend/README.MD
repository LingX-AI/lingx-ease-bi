# Project Setup and Development Guide

## Environment Setup

### Install Dependencies
```shell
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Export current dependencies
pip list --format=freeze > requirements.txt

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
1. Copy `.env.example` to `.env`
2. Configure your environment variables in `.env`

## Database Management

### Migrate Database
```shell
# Generate migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Running the Server

### Development Server
```shell
# Django development server
python manage.py runserver 8000

# Using Uvicorn (recommended for production-like environment)
uvicorn backend.asgi:application --workers 4 --reload --host 0.0.0.0 --port 8000 --env-file .env
```

### Server Parameters
- `--workers 4`: Number of worker processes
- `--reload`: Enable auto-reload on code changes (development only)
- `--host 0.0.0.0`: Listen on all network interfaces
- `--port 8000`: Server port
- `--env-file .env`: Load environment variables from .env file

## Additional Commands

### Create Superuser
```shell
python manage.py createsuperuser
```
