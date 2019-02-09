import requests
import json
import os
import zipfile

class codeez:

    def __init__(self, Account=None, Authorization=None):
        self.Account = Account
        self.url='https://api.codeez.tech/'
        self.Authorization=Authorization

        if Account != None:
            headers={}
            headers['content-type'] = 'application/json'
            headers['account']=self.Account
            response = requests.request("GET", url=self.url + 'mservices', headers=headers)
            self.services = json.loads(response.text)
        else:
            self.services={}

    def create_account(self, email, FirstName, LastName):
        try:
            headers={}
            headers['content-type'] = 'application/json'
            values={'email':email,'FirstName':FirstName,'LastName':LastName}
            response = requests.post(url=self.url + 'accounts', headers=headers, data=json.dumps(values))
            if response.status_code == 200:
                #print(response.text)
                self.Account=json.loads(response.text)['account']
                self.Authorization=json.loads(response.text)['Token']
            else:
                return {"error": response.text, "error_code": response.status_code}
        except:
            1==1

            return json.loads(response.text)

        #return json.loads(response.text)

    def servicelist(self):
        headers = {}
        if headers != None:
            headers['content-type'] = 'application/json'
        else:
            headers = {'content-type': 'application/json'}
        headers['Account'] = self.Account
        try:
            response = requests.get(url=self.url + 'mservices', headers=headers)
        except:
            return {"error": "Something went wrong"}
        return json.loads(response.text)

    def logs(self,ServiceName):
        headers = {}
        if headers != None:
            headers['content-type'] = 'application/json'
        else:
            headers = {'content-type': 'application/json'}
        headers['Account'] = self.Account
        headers['Authorization'] = self.Authorization
        try:
            response = requests.get(url=self.url + 'logs/'+ServiceName, headers=headers)
        except:
            return {"error": "Something went wrong"}
        return json.loads(response.text)

    def execute(self, mservice, function, query=None, headers=None, body=None):

        if body==None:
            if headers == None:
                headers={}

            #if headers == None:
            #    headers['content-type']='application/json'
            #else:
            #    headers = {'content-type':'application/json'}
            try:
                for item in self.services:
                    if item['ServiceName'] == mservice:
                        urlfunction = item['url']
                        #urlfunction = "http://54.68.25.233"
                        #portfunction = item['port']
                        #portfunction = 8000
                response = requests.get(url=urlfunction+"/myfunction/"+str(function), params=query,headers=headers)
                #print(urlfunction, str(portfunction))
                if response.status_code != 200:
                    return {"error": response.content}
            except:
                return {"error":"Something went wrong"}
            #print (json.loads(response.text))
        else:
            if headers == None:
                headers = {}

            #if headers != None:
            #    headers['content-type']='application/json'
            #else:
            #    headers = {'content-type':'application/json'}
            #print ('body',body)
            try:
                for item in self.services:
                    if item['ServiceName'] == mservice:
                        urlfunction = item['url']
                        #urlfunction = "http://54.68.25.233"
                        #portfunction = item['port']
                        #portfunction = 8000
                #print(urlfunction, str(portfunction), str(function), body)

                response = requests.post(url=urlfunction+"/myfunction/"+str(function),params=query, headers=headers, data=body)

                if response.status_code != 200:
                    return {"error": response.text,"error_code":response.status_code}
            except:
                return {"error": "Something went wrong"}
            #print (response.text)

        return response.content

    def create(self,name,directory,type='MService',Description=None,Private=False,DB=False,ServiceName=None,ServiceAccount=None):

        Account= self.Account
        Authorization=self.Authorization
        try:
            os.remove('/tmp/customer.zip')
        except:
            1==1

        try:

            zipf = zipfile.ZipFile('/tmp/customer.zip', 'w', zipfile.ZIP_DEFLATED)
            os.chdir(directory)
            for root, dirs, files in os.walk('.'):
                for file in files:
                    zipf.write(os.path.join(root, file))
            zipf.close()

            os.chdir('/tmp/')
            url=self.url
            files = {'file': open('customer.zip','rb')}
            #print(files)
            values = {'name': name,'Account':Account,'Authorization':Authorization,'Description':Description,'DB':DB,'Private':Private}
        except:
            return {"error":"Something went wrong"}
        try:
            if type=='MService':
                response = requests.post(url=url+"mservices", files=files, data=values)
                #print(response.text)
                self.services=self.servicelist()
                if response.status_code != 200:
                    return {"error": response.text, "error_code": response.status_code}
            elif type=='Site':
                if ServiceName != None and ServiceAccount != None:
                    values['ServiceName']=ServiceName
                    values['ServiceAccount']=ServiceAccount
                response = requests.post(url=url + "sites", files=files, data=values)
                # print(response.text)
                self.services = self.servicelist()
                if response.status_code != 200:
                    return {"error": response.text, "error_code": response.status_code}
        except:
            return {"Error":"something went wrong"}
        try:
            os.remove('/tmp/customer.zip')
        except:
            1==1
        return json.loads(response.text)

    def update(self,name,directory,type='MService',Description=None,DB=False,Private=False,ServiceName=None,ServiceAccount=None):

        Account= self.Account
        Authorization=self.Authorization
        try:
            os.remove('/tmp/customer.zip')
        except:
            1==1

        try:
            zipf = zipfile.ZipFile('/tmp/customer.zip', 'w', zipfile.ZIP_DEFLATED)
            os.chdir(directory)
            for root, dirs, files in os.walk('.'):
                for file in files:
                    zipf.write(os.path.join(root, file))
            zipf.close()

            os.chdir('/tmp/')
            url=self.url
            files = {'file': open('customer.zip','rb')}
            #print(files)
            values = {'name': name,'Account':Account,'Authorization':Authorization,'Description':Description,'DB':DB,'Private':Private}

            if type=='MService':
                #response = requests.post(url=url+"mservices", files=files, data=values)

                response = requests.patch(url=url + "mservices", files=files, data=values)

            elif type=='Site':
                if ServiceName != None and ServiceAccount != None:
                    values['ServiceName']=ServiceName
                    values['ServiceAccount']=ServiceAccount
                response = requests.patch(url=url + "sites", files=files, data=values)

            self.services=self.servicelist()
            if response.status_code != 200:
                return {"error": response.text, "error_code": response.status_code}
        except:
            return {"error": "Something went wrong"}
        try:
            os.remove('/tmp/customer.zip')
        except:
            1==1
        return json.loads(response.text)

    def delete(self,name):

        Account= self.Account
        Authorization=self.Authorization

        try:
            headers = {}
            headers['content-type'] = 'application/json'
            headers['Account']=self.Account
            headers['Authorization']=Authorization
            values = {'name': name}
            response = requests.delete(url=self.url + 'mservices', headers=headers, data=json.dumps(values))
            self.services=self.servicelist()
            if response.status_code != 200:
                return {"error": response.text,"error_code":response.status_code}
        except:
            return {"error": "Something went wrong"}

        return json.loads(response.text)

    def store(self,StorageName,Content):

        Account = self.Account
        Authorization = self.Authorization

        try:
            headers = {}

            headers['Account'] = Account
            headers['Authorization'] = Authorization

            values = Content

            urlfunction = 'https://storage.codeez.tech/myfunction/store?Name='+StorageName

            response = requests.post(url=urlfunction,headers=headers,data=values)
            if response.status_code != 200:
                return {"error": response.content,"error_code":response.status_code}
            else:
                return {"Storage": StorageName, "Status": "Success"}
        except:
            return {"error": "Something went wrong"}

    def retrieve(self, StorageName):

        Account = self.Account
        Authorization = self.Authorization

        try:
            headers = {}

            headers['Account'] = Account
            headers['Authorization'] = Authorization

            urlfunction = 'https://storage.codeez.tech/myfunction/retrieve?Name=' + StorageName

            response = requests.get(url=urlfunction, headers=headers)
            if response.status_code != 200:
                return {"error": response.content, "error_code": response.status_code}
            else:
                return response.content
        except:
            return {"error": "Something went wrong"}

