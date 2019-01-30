from guillotina import testing


def base_settings_configurator(settings):
    if 'applications' in settings:
        settings['applications'].append('guillotina_pgcatalog')
    else:
        settings['applications'] = ['guillotina_pgcatalog']

    settings["load_utilities"]['catalog'] = {
        "provides": "guillotina.interfaces.ICatalogUtility",
        "factory": "guillotina_pgcatalog.utility.PGSearchUtility"
    }


testing.configure_with(base_settings_configurator)
