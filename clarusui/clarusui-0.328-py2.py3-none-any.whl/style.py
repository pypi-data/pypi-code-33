from six import string_types
from clarusui import utils

class Style(object):
    def __init__(self, **options):
        self._colours = None
        self._setColours(options.pop('colours', None))
        self._bgColour = options.pop('backgroundColour')
        self._fgColour = options.pop('foregroundColour')
        self._fontColour = options.pop('fontColour')
        self._fontFamily = options.pop('fontFamily', 'Roboto, sans-serif')
        self._borderColour = options.pop('borderColour')
        self._chartTheme = options.pop('chartTheme', None)
        self._tableCssClass = options.pop('tableCssClass', '')
        
    def _setColours(self, colours):
        if isinstance(colours, string_types):
            decoded = utils.get_colour_set(colours)
            if decoded is None:
                raise ValueError('Specify a list of colours or one of: '+ str(list(utils.COLOURS)))
            self._colours = decoded
        if isinstance(colours, list):
            self._colours = colours

    def getBackgroundColour(self):
        return self._bgColour

    def getForegroundColour(self):
        return self._fgColour

    def getFontColour(self):
        return self._fontColour

    def getBorderColour(self):
        return self._borderColour

    def getFontFamily(self):
        return self._fontFamily
    
    def getChartTheme(self):
        return self._chartTheme
    
    def getTableCssClass(self):
        return self._tableCssClass
    
    def getColours(self):
        return self._colours
    
            
class DarkStyle(Style):
    def __init__(self, backgroundColour='#000000', foregroundColour='#111111', fontColour='white', borderColour='#3E3E3E', tableCssClass='table-inverse',  **options):
        super(DarkStyle, self).__init__(backgroundColour=backgroundColour, 
                                        foregroundColour=foregroundColour, fontColour=fontColour, borderColour=borderColour, tableCssClass=tableCssClass, **options)
        
class DarkBlueStyle(Style):
    def __init__(self, backgroundColour='#252830', foregroundColour='#111111', fontColour='white', borderColour='#434857', tableCssClass='table-inverse', **options):
        super(DarkBlueStyle, self).__init__(backgroundColour=backgroundColour, 
                                        foregroundColour=foregroundColour, fontColour=fontColour, borderColour=borderColour, tableCssClass=tableCssClass, **options)

class LightStyle(Style):
    def __init__(self, backgroundColour='white', foregroundColour='white', fontColour='#555555', borderColour='#e9ecef', **options):
        super(LightStyle, self).__init__(backgroundColour=backgroundColour, 
                                        foregroundColour=foregroundColour, fontColour=fontColour, borderColour=borderColour, **options)

def getAutoStyle(event, colours):
    if event is None or event.get('__theme') != 'default':
        return DarkStyle(colours=colours)
    return LightStyle(colours=colours)
	