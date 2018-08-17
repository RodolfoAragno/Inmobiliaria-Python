import os
import dj_database_url
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if 'SECRET_KEY' in os.environ:
	SECRET_KEY = os.environ.get('SECRET_KEY')
else:
	with open(os.path.join(BASE_DIR, 'error-log.txt'), 'a') as f:
		from datetime import datetime
		f.write('{}: {}{}'.format(datetime.now().isoformat(), 'Error en SECRET_KEY.', os.linesep))
		f.close()
	raise Exception('No se ha fijado la clave secreta.')
if 'DATABASE_URL' not in os.environ:
	with open(os.path.join(BASE_DIR, 'error-log.txt'), 'a') as f:
		from datetime import datetime
		f.write('{}: {}{}'.format(datetime.now().isoformat(), 'Error en DATABASE_URL.', os.linesep))
		f.close()
	raise Exception('No se ha fijado la url de la base de datos.')

DEBUG = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'gazze.in']
INSTALLED_APPS = [
    'django.contrib.auth',
	'django.contrib.staticfiles',
    'django.contrib.contenttypes',
    'widget_tweaks',
    'personas',
    'propiedades',
    'contratos',
    'parametros',
    'ajax',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'allow_cidr.middleware.AllowCIDRMiddleware',
]
ALLOWED_CIDR_NETS = ['192.168.0.1/24']
ROOT_URLCONF = 'inmobiliaria.urls'
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
DATABASES = {
    'default': dj_database_url.config(default='postgres://')
}
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'min_length': 3,
        }
    },
]
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'gazze_documentos')
os.environ.setdefault('MEDIA_ROOT', MEDIA_ROOT)