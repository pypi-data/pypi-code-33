from operations import *
from expdict import *
from includeexclude import *
from checkexpiry import *


class Rotate:

    def rotatekeys(self):
        for user in obj3.userList:
            print user
            rep1 = obj4.excludeuser(user)
            rep2 = obj4.includeuser(user)
            if rep1 == True:
            	print ("USER IS BLACKLISTED")
            	continue

            print ("USER IS WHITELISTED")
            obj2.listkey(user)
            print("ORIGINAL id List is", obj3.idList)


            if len(obj3.idList) == 1:
                obj2.createkey(user)
            else:
                rep3 = obj5.checkexpiry(user)
                if rep3 == True:
                    obj2.rotatekey(user)
            obj2.updateList(user)
            del obj3.idList[:]


obj=Rotate()
print("PREPARE includeuser.txt and excludeuser.txt FILES")

obj2.listuser()
print obj3.userList

obj.rotatekeys()