# S2I Deployment Documentation

## Overview

This repository contains a Django CRM application that is designed to be deployed using Source-to-Image (S2I) approach with Red Hat UBI9 Python 3.12 container image.

## Base Image

- **Image**: `ubi9/python-312` (Red Hat Universal Base Image 9 with Python 3.12)
- **Registry**: `registry.access.redhat.com/ubi9/python-312` or `registry.redhat.io/ubi9/python-312`
- **Documentation**: https://catalog.redhat.com/en/software/containers/ubi9/python-312/657b08d023df896ebfacf402

**Note**: The infrastructure repository may reference `python-311` in examples, but this codebase uses Python 3.12.

## Repository Structure

```
engineering-work-crm/
├── docs/                    # Documentation
├── requirements.txt         # Python dependencies (root level)
├── source/
│   └── minicrm/            # Django application (S2I source context)
│       ├── manage.py
│       ├── requirements.txt # Python dependencies (for S2I)
│       ├── minicrm/        # Django project settings
│       │   ├── settings.py
│       │   ├── wsgi.py     # WSGI application entry point
│       │   └── urls.py
│       ├── customer/       # Customer app
│       ├── product/         # Product app
│       └── order/          # Order app
└── .venv/                  # Local virtual environment (not deployed)
```

## S2I Build Process

The S2I builder will:

1. **Copy source code** from `source/minicrm/` to `/opt/app-root/src` in the container
2. **Install dependencies** from `requirements.txt` using pip
3. **Detect WSGI application** from `minicrm/wsgi.py` (automatically detects `application` variable)
4. **Run the application** using Gunicorn on port 8080 (container port)

## Deployment Method

**Note**: This application is deployed via **ArgoCD and Kubernetes**, not using direct S2I commands. The S2I build process happens automatically as part of the Kubernetes/ArgoCD deployment workflow.

For local testing or manual builds, you can use S2I CLI (if available):

```bash
s2i build https://github.com/DawidAdamski/engineering-work-crm.git \
  --context-dir=source/minicrm \
  registry.access.redhat.com/ubi9/python-312 \
  crm-api:latest
```

However, in production, the build and deployment are managed by:
- **ArgoCD** for GitOps-based deployment
- **Kubernetes BuildConfig** (if using OpenShift) or similar CI/CD pipeline
- See the infrastructure repository for deployment manifests: `/home/dadamski/praca_inzynierska/engineering-work-infrastracture/`

## Environment Variables

### S2I Builder Variables

The S2I builder supports the following environment variables (can be set in `.s2i/environment` file or via Kubernetes/ArgoCD):

- **APP_MODULE**: WSGI module path (defaults to auto-detection from `wsgi.py`)
  - Example: `minicrm.wsgi:application`
- **DISABLE_MIGRATE**: Set to non-empty value to skip `manage.py migrate` on startup
- **DISABLE_COLLECTSTATIC**: Set to non-empty value to skip `manage.py collectstatic` during build
- **APP_HOME**: Sub-directory containing the application (if not root)

### Django Application Variables

The Django application uses the following environment variables (set via Kubernetes ConfigMap/Secrets):

**Database Configuration** (supports both naming conventions):
- `POSTGRES_HOST` or `DB_HOST` - PostgreSQL hostname (e.g., `postgres.crm-rfm.svc.cluster.local`)
- `POSTGRES_DB` or `DB_NAME` - Database name (e.g., `crmdb`)
- `POSTGRES_USER` or `DB_USER` - Database user
- `POSTGRES_PASSWORD` or `DB_PASSWORD` - Database password
- `POSTGRES_PORT` or `DB_PORT` - Database port (default: `5432`)
- `DB_ENGINE` - Set to `postgresql` to enable PostgreSQL (alternative to `POSTGRES_HOST`)

**Django Settings**:
- `SECRET_KEY` - Django secret key (required in production)
- `DEBUG` - Set to `False` in production
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts

**Other Services** (for future AI/Qdrant integration):
- `QDRANT_URL` - Qdrant API endpoint
- `QDRANT_COLLECTION` - Collection name for embeddings
- `OPENAI_MODEL` - Embedding model name
- `LOG_LEVEL` - Logging level (default: `INFO`)

## Django Configuration for Production

### Required Settings Updates

Before deploying to production, update `source/minicrm/minicrm/settings.py`:

1. **SECRET_KEY**: Use environment variable or secret management
2. **DEBUG**: Set to `False`
3. **ALLOWED_HOSTS**: Add your domain(s)
4. **Database**: Configure production database (PostgreSQL recommended)
5. **Static Files**: Configure static file serving
6. **Security Settings**: Enable HTTPS, CSRF protection, etc.

### Example Production Settings

```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database configuration (example for PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = '/opt/app-root/static'
STATIC_URL = '/static/'
```

## ArgoCD Deployment

This application is deployed using ArgoCD. Refer to the infrastructure repository for ArgoCD configuration:

- Infrastructure Repository: `/home/dadamski/praca_inzynierska/engineering-work-infrastracture/`
- Documentation: `README.crm-api.md`

### ArgoCD Application Configuration

The ArgoCD application should:
- Use S2I build strategy
- Set build context to `source/minicrm`
- Configure environment variables for Django settings
- Set up database connection secrets
- Configure health checks and probes

## Local Development

### Setup with uv

1. **Create virtual environment**:
   ```bash
   uv venv
   ```

2. **Activate virtual environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   cd source/minicrm
   python manage.py migrate
   ```

5. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## Application Endpoints

- **Admin Panel**: `/admin/`
- **API Root**: `/api/`
- **Customers API**: `/api/customers/`
- **Products API**: `/api/products/`
- **Orders API**: `/api/orders/`

## Dependencies

All Python dependencies are listed in `requirements.txt`:

- Django 5.1.7
- Django REST Framework 3.16.0
- django-filter 25.1
- And other supporting packages

## Port Configuration

- **Container Port**: The S2I builder runs the application on port **8080** inside the container (S2I default)
- **Kubernetes Service Port**: The Kubernetes service exposes port **8000** (as configured in deployment manifests)
- The port mapping (8080 → 8000) is handled by the Kubernetes Service configuration

## Health Checks

Configure health checks in OpenShift/Kubernetes:

- **Liveness Probe**: HTTP GET `/api/` (or appropriate endpoint)
- **Readiness Probe**: HTTP GET `/api/` (or appropriate endpoint)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in `requirements.txt`
2. **Database Connection**: Verify database credentials and network connectivity
3. **Static Files**: Run `collectstatic` during build or configure static file serving
4. **Migrations**: Ensure migrations run on startup or disable with `DISABLE_MIGRATE`

### Viewing Logs

```bash
# OpenShift
oc logs <pod-name>

# Kubernetes
kubectl logs <pod-name>
```

## References

- [Red Hat UBI9 Python 3.12 Documentation](https://catalog.redhat.com/en/software/containers/ubi9/python-312/657b08d023df896ebfacf402)
- [S2I Python Container](https://github.com/sclorg/s2i-python-container)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)

