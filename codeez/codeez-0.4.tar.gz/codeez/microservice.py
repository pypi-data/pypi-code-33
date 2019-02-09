class microservice:

    def __init__(self):

        return None

    def execute(self, url, function, query=None, headers=None, body=None):

        if body==None:
            if headers == None:
                headers={}

            try:

                response = requests.get(url=url+"/myfunction/"+str(function), params=query,headers=headers)
                #print(urlfunction, str(portfunction))
                if response.status_code != 200:
                    return {"error": response.content}

            except:
                return {"error":"Something went wrong"}
            #print (json.loads(response.text))
        else:
            if headers == None:
                headers={}

            try:

                response = requests.post(url=url+"/myfunction/"+str(function),params=query, headers=headers, data=body)

                if response.status_code != 200:
                    return {"error": response.content,"error_code":response.status_code}
            except:
                return {"error": "Something went wrong"}
            #print (response.text)

        return response.content


