SECRET_KEY = '1978'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'dgenome',
    'dmethylation'
]

ROOT_URLCONF = 'dmethylation.tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
