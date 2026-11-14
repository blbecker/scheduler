FROM python:3.12-slim@sha256:a0f57064cbdcd6285fa45f51237ab0b35ea8ebaed06a1f5973e89e19dfb86704

# Create a non-root user with UID/GID 1000
RUN groupadd -g 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash appuser

# set workdir
WORKDIR /app

# install deps
RUN pip install --upgrade pip

# copy base requirements first for caching
COPY requirements-base.txt .
RUN pip install -r requirements-base.txt

# copy source
COPY . .

ENV PYTHONUNBUFFERED=1

# Switch to the non-root user
USER appuser

# expose port
EXPOSE 8000

# run production server with workers
CMD ["uvicorn", "scheduler_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]