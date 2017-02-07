# Choose settings between Development and Production
import os
import platform

node = platform.node()
dev_machines = ('Henrys-MacBook-Pro.local', 'Henrys-MBP')
prod_machines = ('vultr.guest')

if node in dev_machines:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    ALLOWED_HOSTS = ['*']
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    INTERNAL_IPS = (
        '0.0.0.0',
        '127.0.0.1',
    )
else:
    DEBUG = False
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME'),
	        'USER': os.environ.get('DB_USER'),
	        'PASSWORD': os.environ.get('DB_PASSWORD'),
	        'HOST': 'localhost',
	        'PORT': '',
        }
    }
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.henry-olson.com']
    SECURE_SSL_REDIRECT = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    INTERNAL_IPS = ()