import requests, json, urllib.parse, datetime

auth_url = 'https://mit.seas-nve.dk'
base_url = 'https://msn-api.seas-nve.dk/api/v1.0'

class seas:

    def __init__(self, EMAIL, PASSWORD):
        global s, authheader
        s = requests.Session()
        login_payload = 'Email='+urllib.parse.quote(EMAIL)+'&Password='+PASSWORD+'&RememberMe=false'
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        try:
            s.post(auth_url+'/Login/Username',data=login_payload, headers=headers)
            d = s.cookies.get("MSNSSOCookie")
            Bearer = 'Bearer '+d
            authheader = {'Authorization': Bearer}
        except:
            error = 1
            print('error')

    def logout(self):
        s.get(auth_url+'/Login/Logout', allow_redirects=False)

    def meteringPointNumber(self):
        # Will return meteringPoint which is needed for meteringPoints requests
        m = requests.get(base_url+'/profile/metering/', headers=authheader)
        data = m.json()[0]
        meteringPoint = data['meteringPoint']
        return meteringPoint

    def consumptionYearToDate(self):
        now = datetime.datetime.now()
        mpn = self.meteringPointNumber()
        m = requests.get(base_url+'/profile/consumption/?meteringpoints='+mpn+'&start='+str(now.year)+'-01-01&end='+str(now.year)+'-12-31&aggr=Year', headers=authheader)
        data = m.json()
        self.logout()
        return data
        
    def meteringPoints(self,aggr,start,end):
        # Valid aggr is Hour, Day, Month, Year
        mpn = self.meteringPointNumber()
        m = requests.get(base_url+'/profile/consumption/?meteringpoints='+mpn+'&start='+start+'&end='+end+'&aggr='+aggr+'', headers=authheader)
        data = m.json()
        self.logout()
        return data