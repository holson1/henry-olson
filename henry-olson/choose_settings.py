# Choose settings between Development and Production
import os
import platform

node = platform.node()
dev_machines = ('Henrys-MacBook-Pro.local')
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
    ALLOWED_HOSTS = [
        'vultr.guest'
    ]