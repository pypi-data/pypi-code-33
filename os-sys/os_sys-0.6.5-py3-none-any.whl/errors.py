class WifiError(Exception):
    'a wifi error was found or raised'
    pass
class NoResponseError(WifiError):
    'no response from server site or somting'
