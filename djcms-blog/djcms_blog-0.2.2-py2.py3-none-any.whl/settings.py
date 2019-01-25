from django.conf import settings

LANGUAGES = getattr(settings, "LANGUAGES", None)
LANGUAGE_CODE = getattr(settings, "LANGUAGE_CODE", None)
DEFAULT_BLOG_ID = getattr(settings, "DEFAULT_BLOG_ID", None)

assert LANGUAGES, "django LANGUAGES must be defined in settings.py"
assert LANGUAGE_CODE, "django LANGUAGE_CODE must be defined in settings.py"

DEFAULT_URL = getattr(settings, "DJCMS_BLOG_DEFAULT_URL", "#")

BLOG_TITLE = getattr(settings, "DJCMS_BLOG_TITLE", "Django Blog")  # Used in html title

ROOT_TITLE = getattr(settings, "DJCMS_BLOG_ROOT_TITLE", "Django Blog")  # Used in links to home page as string

DJCMS_BLOG_CACHE_TIME = getattr(settings, "DJCMS_BLOG_CACHE_TIME", 60 * 60 * 24)

MARKDOWN_CODE_CSS_THEME = getattr(settings, "DJCMS_BLOG_MARKDOWN_CODE_CSS_THEME", 'dracula')

STATIC_URL = settings.STATIC_URL

DEFAULT_COVER_IMAGE = getattr(
    settings,
    "DJCMS_BLOG_DEFAULT_COVER_IMAGE",
    f"{STATIC_URL}djcms_blog/img/index-bg.jpg"
)  # User as default cover image

DEFAULT_NAVBAR_IMAGE = getattr(
    settings,
    "DJCMS_BLOG_NAVBAR_IMAGE",
    f"{STATIC_URL}djcms_blog/img/default-blog-navicon.jpg"
)  # Used in navbar

DEFAULT_USER_PROFILE_IMAGE = getattr(
    settings,
    "DEFAULT_USER_PROFILE_IMAGE",
    f"{STATIC_URL}djcms_blog/img/default-blog-user-profile.jpg"
)  # Used in navbar
