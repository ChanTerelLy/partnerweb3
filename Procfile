release: python manage.py migrate
web: gunicorn partnerweb_project.wsgi --log-file=- & node autoping.js
worker: celery worker --beat --app=partnerweb_project
