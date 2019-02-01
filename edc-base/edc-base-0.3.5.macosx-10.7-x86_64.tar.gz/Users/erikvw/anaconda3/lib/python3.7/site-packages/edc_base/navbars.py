from edc_navbar import Navbar, NavbarItem, site_navbars


consent = Navbar(name="edc_base")

consent.append_item(
    NavbarItem(
        name="edc_base",
        label="Edc Base",
        fa_icon="fa-cogs",
        permission_codename="edc_navbar.nav_edc_base",
        url_name="edc_base:home_url",
    )
)

site_navbars.register(consent)
