from datetime import datetime
from expdict import *

class Expiry:

	validdays = raw_input("Enter no. of valid days ")


	def checkexpiry(self, user):
	    if(obj3.dateList[1] > obj3.dateList[0]):
	        createdate = obj3.dateList[0]
	    else:
	        createdate = obj3.dateList[1]
	    currentdate = datetime.now().replace(microsecond=0)
	    delta = currentdate - createdate
	    if int(delta.days) >= int(Expiry.validdays):
	        return True
	    return False


obj5=Expiry()
