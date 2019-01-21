
import voluptuous as vol


CONF_RESOURCES = 'resources'
CONF_UNIVERSE = 'universe'
CONF_TYPE = 'type'
CONF_PORT = 'port'
CONF_DEBUG = 'debug'
CONF_VERSION = 'version'

DEFAULT_DEBUG = False
DEFAULT_VERSION = '1.4'



CONFIG_SCHEMA = vol.Schema({
  DOMAIN: vol.Schema({
    vol.Required(CONF_RESOURCES): vol.All(cv.ensure_list, [
      {
        vol.Required(CONF_UNIVERSE): cv.positive_int,
        vol.Required(CONF_PORT): cv.string,
        vol.Required(CONF_TYPE): vol.In(['IN', 'in', 'In', 'OUT', 'out', 'Out'])
      },
    ]),
    vol.Optional(CONF_DEBUG, default=DEFAULT_DEBUG): cv.boolean,
    vol.Optional(CONF_VERSION, default=DEFAULT_VERSION): cv.string,
  })
}, extra=vol.ALLOW_EXTRA)

