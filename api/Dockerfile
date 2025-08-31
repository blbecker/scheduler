FROM python:3.12-slim@sha256:d67a7b66b989ad6b6d6b10d428dcc5e0bfc3e5f88906e67d490c4d3daac57047

# set workdir
WORKDIR /app

# install deps
RUN pip install --upgrade pip

# copy requirements first for caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy source
COPY . .

ENV PYTHONUNBUFFERED=1

# expose dev port
EXPOSE 8000

# run dev server with autoreload
CMD ["uvicorn", "scheduler_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
