FROM python:3.12-slim

# set workdir
WORKDIR /app

# install deps
RUN pip install --upgrade pip

# copy requirements first for caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy source
COPY . .

# env vars for Django dev
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=scheduler_api.settings

# expose dev port
EXPOSE 8000

# run dev server with autoreload
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
