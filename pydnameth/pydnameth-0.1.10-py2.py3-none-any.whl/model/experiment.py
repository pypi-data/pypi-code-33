from pydnameth.model.context import Context


def base(config):
    config.initialize()
    context = Context(config)
    context.base_pipeline(config)


def advanced(config, configs_primary):
    config.initialize()
    for config_primary in configs_primary:
        config_primary.initialize()
    context = Context(config)
    context.advanced_pipeline(config, configs_primary)


def plot(config, configs_primary):
    config.initialize()
    for config_primary in configs_primary:
        config_primary.initialize()
    context = Context(config)
    context.plot_pipeline(config, configs_primary)


__all__ = ['base', 'advanced', 'plot']
