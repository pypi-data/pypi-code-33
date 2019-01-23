from lbmessaging.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.CvmfsConDBExchange import CvmfsConDBExchange
from lbmessaging.CvmfsProdExchange import CvmfsProdExchange

exchangeManager = {
	'CvmfsDevExchange': CvmfsDevExchange,
	'CvmfsConDBExchange': CvmfsConDBExchange,
	'CvmfsProdExchange': CvmfsProdExchange
}