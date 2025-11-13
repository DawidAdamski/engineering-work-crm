# Use Fedora 42 base image
FROM docker.io/fedora:42

# Set working directory
WORKDIR /app

# Install system dependencies using dnf
RUN dnf install -y --setopt=install_weak_deps=False \
        python3.12 \
        python3.12-devel \
        gcc \
        postgresql \
        postgresql-devel \
        curl \
        && \
    dnf clean all

# Install uv (fast Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Copy requirements first for better layer caching
COPY source/minicrm/requirements.txt .

# Install Python dependencies using uv
RUN uv pip install --system -r requirements.txt

# Copy application source code
COPY source/minicrm/ .

# Make startup script executable (it's already copied with source code)
RUN chmod +x /app/start.sh

# Collect static files (can be disabled with DISABLE_COLLECTSTATIC env var)
# Run as root before switching to non-root user
RUN if [ -z "$DISABLE_COLLECTSTATIC" ]; then \
        python manage.py collectstatic --noinput || true; \
    fi

# Create non-root user and set ownership
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8080 (Kubernetes service will map to 8000)
EXPOSE 8080

# Set default command to run startup script
ENV APP_MODULE=minicrm.wsgi:application

# Use startup script that handles migrations
CMD ["/app/start.sh"]

