ROOT_URLCONF='tests.urls'
SECRET_KEY='---foobar--'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    'NAME': ':memory:',
    }
}
MANAGERS=('foobar@example.com',)
ALLOWED_HOSTS = ['testserver']

DEBUG=False
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

MIDDLEWARE = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
)
