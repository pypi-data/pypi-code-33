import clarus.services

def activity(output=None, **params):
    return clarus.services.api_request('Util', 'Activity', output=output, **params)

def discovery(output=None, **params):
    return clarus.services.api_request('Util', 'Discovery', output=output, **params)

def domain(output=None, **params):
    return clarus.services.api_request('Util', 'Domain', output=output, **params)

def financialcenters(output=None, **params):
    return clarus.services.api_request('Util', 'FinancialCenters', output=output, **params)

def grid(output=None, **params):
    return clarus.services.api_request('Util', 'Grid', output=output, **params)

def periodlength(output=None, **params):
    return clarus.services.api_request('Util', 'PeriodLength', output=output, **params)

def report(output=None, **params):
    return clarus.services.api_request('Util', 'Report', output=output, **params)

def tickers(output=None, **params):
    return clarus.services.api_request('Util', 'Tickers', output=output, **params)

