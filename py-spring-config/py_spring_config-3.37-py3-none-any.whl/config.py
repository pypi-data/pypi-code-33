from dynaconf import LazySettings


def load_config(env):
    if env == 'local':
        dynaconf_settings = LazySettings(SETTINGS_MODULE_FOR_DYNACONF="settings.toml")
        dynaconf_settings.setenv('local')
    else:
        dynaconf_settings = LazySettings(SETTINGS_MODULE_FOR_DYNACONF="settings.toml",
                                         LOADERS_FOR_DYNACONF=['py_spring_config.loader',
                                                               'dynaconf.loaders.toml_loader',
                                                               'dynaconf.loaders.env_loader'])
        dynaconf_settings.setenv('production')

    return dynaconf_settings
