
class Style(object):
    def __init__(self, **options):
        self._bgColour = options.pop('backgroundColour')
        self._fgColour = options.pop('foregroundColour')
        self._fontColour = options.pop('fontColour')
        self._fontFamily = options.pop('fontFamily', 'Roboto, sans-serif')
        self._borderColour = options.pop('borderColour')
        self._chartTheme = options.pop('chartTheme', None)

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

class DarkStyle(Style):
    def __init__(self):
        super(DarkStyle, self).__init__(backgroundColour='#000000', 
                                        foregroundColour='#111111', fontColour='white', borderColour='#3E3E3E')
        
class DarkBlueStyle(Style):
    def __init__(self):
        super(DarkBlueStyle, self).__init__(backgroundColour='#252830', 
                                            foregroundColour='#111111', fontColour='white', borderColour='#434857')

class LightStyle(Style):
    def __init__(self):
        super(LightStyle, self).__init__(backgroundColour='white', 
                                         foregroundColour='white', fontColour='#555555', borderColour='#e9ecef')


	