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

ENV PYTHONUNBUFFERED=1

# expose dev port
EXPOSE 8000

# run dev server with autoreload
CMD ["uvicorn", "scheduler_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
