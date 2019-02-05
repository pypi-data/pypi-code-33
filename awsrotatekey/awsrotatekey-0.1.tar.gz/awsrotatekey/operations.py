from expdict import *

import boto3

class Operations:
    iam_client = boto3.client('iam')

    def listuser(self):
        ndict2 = Operations.iam_client.list_users()
        obj3.expdict2(ndict2, 'Users')


    def createkey(self, user):
        ndict3 = Operations.iam_client.create_access_key(UserName=user)
        obj3.expdict3(ndict3)


    def listkey(self, user):
        ndict = Operations.iam_client.list_access_keys(UserName=user)
        obj3.expdict(ndict)


    def deletekey(self, user, index):
        Operations.iam_client.delete_access_key(UserName=user, AccessKeyId=obj3.idList[index])


    def rotatekey(self, user):
        if obj3.dateList[0] > obj3.dateList[1]:
            self.deletekey(user, 1)
            self.createkey(user)
        else:
            self.deletekey(user, 0)
            self.createkey(user)
        print("SUCCESS")


    def updateList(self, user):
        del obj3.idList[:]
        del obj3.dateList[:]
        self.listkey(user)
        print("THE NEW UPDATED ID LIST IS", obj3.idList)


obj2=Operations()