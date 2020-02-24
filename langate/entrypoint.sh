cp /app/theming/langate.css static/css/
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
gunicorn langate.wsgi -b 0.0.0.0:8000
