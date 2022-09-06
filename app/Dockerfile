FROM python:3.10-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app

WORKDIR /app
RUN pip install -r requirements.txt
RUN python manage.py migrate
RUN python manage.py loaddata ./products/fixtures/*

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
