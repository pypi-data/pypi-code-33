import os

from django.conf import settings
from string import Template

ID = 0
NAME = 1

filename_template = '$site_name.$app_name.$domain.conf'

template = """# nginx.conf

server {
   listen 80;
   server_name $site_name.$app_name.$domain;
   listen [::]:80;
   return 301 https://$server_name$request_uri;
}
server {
   # SSL configuration
   server_name $site_name.$app_name.$domain;
   listen 443 ssl http2;
   listen [::]:443 ssl http2;
   include snippets/self-signed.conf;
   include snippets/ssl-params.conf;

   # logging
   access_log /var/log/$app_name-nginx-access.log;
   error_log /var/log/$app_name-nginx-error.log;
   location = /favicon.ico {
       access_log off; log_not_found off;
   }
   # static files
   location /static/ {
      alias /home/django/source/static/;
   }
   # proxy
   location / {
      proxy_pass http://127.0.0.1:90$site_id;
   }
}"""


def create_nginx_conf_files(path=None, sites=None, domain=None):
    """Generates nginx conf files for each site.

    Copy new conf files to /etc/nginx/sites-available.

    "sites" is a tuple of ((site_id, site_name), ...)

    for example:
        $ python manage.py shell
        >>> import os
        >>> from edc_base.config import create_nginx_conf_files
        >>> from ambition_sites import ambition_sites
        >>> path = os.path.expanduser('~/source/ambition/nginx')
        >>> create_nginx_conf_files(path=path, sites=ambition_sites)
    """
    app_name = settings.APP_NAME
    domain = domain or 'clinicedc.org'
    for site in sites:
        site_id = str(site[ID]).zfill(2)
        s = Template(template).safe_substitute(
            site_name=site[NAME], site_id=site_id,
            app_name=app_name, domain=domain)
        filename = Template(filename_template).safe_substitute(
            site_name=site[NAME], app_name=app_name, domain=domain)
        with open(os.path.join(path, filename), 'w+') as f:
            f.write(s)
