release: python manage.py migrate
web: gunicorn partnerweb_project.wsgi --bind=0.0.0.0:$PORT --timeout 1800 --log-file - & node autoping.js
worker: celery worker --app=partnerweb_project
