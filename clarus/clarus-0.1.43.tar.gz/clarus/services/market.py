import clarus.services

def curveusage(output=None, **params):
    return clarus.services.api_request('Market', 'CurveUsage', output=output, **params)

def df(output=None, **params):
    return clarus.services.api_request('Market', 'DF', output=output, **params)

def fixings(output=None, **params):
    return clarus.services.api_request('Market', 'Fixings', output=output, **params)

def futures(output=None, **params):
    return clarus.services.api_request('Market', 'Futures', output=output, **params)

def fxrates(output=None, **params):
    return clarus.services.api_request('Market', 'FXRates', output=output, **params)

def fxvolsurface(output=None, **params):
    return clarus.services.api_request('Market', 'FXVolSurface', output=output, **params)

def inflationrates(output=None, **params):
    return clarus.services.api_request('Market', 'InflationRates', output=output, **params)

def pardv01(output=None, **params):
    return clarus.services.api_request('Market', 'ParDV01', output=output, **params)

def parrates(output=None, **params):
    return clarus.services.api_request('Market', 'ParRates', output=output, **params)

def riskfreerates(output=None, **params):
    return clarus.services.api_request('Market', 'RiskFreeRates', output=output, **params)

def seasonality(output=None, **params):
    return clarus.services.api_request('Market', 'Seasonality', output=output, **params)

def swaptionvolsurface(output=None, **params):
    return clarus.services.api_request('Market', 'SwaptionVolSurface', output=output, **params)

def zerorates(output=None, **params):
    return clarus.services.api_request('Market', 'ZeroRates', output=output, **params)

