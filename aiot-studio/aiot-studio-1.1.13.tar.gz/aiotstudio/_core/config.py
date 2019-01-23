try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser

class AIOTConfigParser(ConfigParser):
    # this was made to avoid stripping internal quotes in the configurations (like inside the token for example... )
    # stripping only the start and end of fully-quoted values and trimming. For example:
    # ' http://i.am.url ' => http://i.am.url
    # "http://i.am.url" => http://i.am.url
    # http://i.am.url => http://i.am.url
    def getQuotedConfig(self, section, option):
        val = self.get(section, option)
        if val.startswith('"') and val.endswith('"') :
            return val[1:-1].strip()
        if val.startswith("'") and val.endswith("'") :
            return val[1:-1].strip()
        else:
            return val.strip()