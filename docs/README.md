# Engineering Work CRM - Documentation

## Overview

This is a Django-based CRM (Customer Relationship Management) application built for engineering work management. The application provides RESTful APIs for managing customers, products, and orders.

## Table of Contents

- [S2I Deployment Guide](S2I_DEPLOYMENT.md) - Complete guide for deploying using Source-to-Image
- [Local Development](#local-development)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)

## Local Development

### Prerequisites

- Python 3.12+
- uv (Python package manager)
- Virtual environment

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd engineering-work-crm
   ```

2. **Create and activate virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Navigate to Django project**:
   ```bash
   cd source/minicrm
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## Project Structure

```
engineering-work-crm/
├── docs/                    # Documentation
│   ├── README.md           # This file
│   └── S2I_DEPLOYMENT.md   # S2I deployment guide
├── source/
│   └── minicrm/            # Django application
│       ├── manage.py        # Django management script
│       ├── requirements.txt # Python dependencies
│       ├── minicrm/         # Django project package
│       │   ├── settings.py  # Django settings
│       │   ├── urls.py      # URL configuration
│       │   └── wsgi.py      # WSGI application
│       ├── customer/        # Customer management app
│       ├── product/         # Product management app
│       └── order/           # Order management app
├── requirements.txt         # Root level dependencies
└── .venv/                   # Virtual environment (local)
```

## API Documentation

### Endpoints

- **Admin Panel**: `/admin/` - Django admin interface
- **API Root**: `/api/` - API root endpoint
- **Customers**: `/api/customers/` - Customer management
- **Products**: `/api/products/` - Product management
- **Orders**: `/api/orders/` - Order management

### API Features

- RESTful API using Django REST Framework
- Pagination (10 items per page)
- Filtering support via django-filter
- Admin interface for data management

## Deployment

This application is designed for deployment using:

- **S2I (Source-to-Image)** with Red Hat UBI9 Python 3.12
- **ArgoCD** for GitOps-based deployment
- **OpenShift/Kubernetes** as the target platform

See [S2I_DEPLOYMENT.md](S2I_DEPLOYMENT.md) for detailed deployment instructions.

## Dependencies

Key dependencies:

- **Django 5.1.7** - Web framework
- **Django REST Framework 3.16.0** - REST API framework
- **django-filter 25.1** - Advanced filtering for DRF

See `requirements.txt` for complete list.

## Development Tools

- **uv** - Fast Python package manager (replaces pip)
- **Django Admin** - Built-in admin interface
- **Django REST Framework** - API framework with browsable API

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally
4. Submit a pull request

## License

[Add license information here]

