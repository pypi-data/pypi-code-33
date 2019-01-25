#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '1'
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',

    'django.contrib.sitemaps',  # Required!
    'dj_markdown',  # Required to support markdown

    'djcms_blog',
)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['', ],
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
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
}

LANGUAGE_CODE = 'en'

LANGUAGES = [
    ('es', 'Español'),
    ('en', 'English'),
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tests.urls'

DJCMS_BLOG_DEFAULT_URL = "#"
DJCMS_BLOG_ROOT_SLUG = 'myblog'
DJCMS_BLOG_TITLE = "Test Blog"
DJCMS_BLOG_ROOT_TITLE = "MyBlog.com"
DJCMS_BLOG_ROOT_URL = "/"
DJCMS_BLOG_MARKDOWN_CODE_CSS_THEME = "dracula"
SITE_ID = 1
STATIC_URL = '/static/'
