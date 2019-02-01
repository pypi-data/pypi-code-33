from django.contrib.admin import AdminSite


class EdcBaseAdminSite(AdminSite):
    site_header = "EdcBase"
    site_title = "EdcBase"
    index_title = "EdcBase Administration"
    site_url = "/administration/"


edc_base_admin = EdcBaseAdminSite(name="edc_base_admin")
