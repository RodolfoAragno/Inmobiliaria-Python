git pull
python manage.py makemigrations contratos
python manage.py makemigrations parametros
python manage.py makemigrations personas
python manage.py makemigrations propiedades
python manage.py migrate
gunicorn -w 4 inmobiliaria.wsgi