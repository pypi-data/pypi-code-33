from lbmessaging.exchanges.CvmfsDevExchange import CvmfsDevExchange
from lbmessaging.exchanges.CvmfsConDBExchange import CvmfsConDBExchange
from lbmessaging.exchanges.CvmfsProdExchange import CvmfsProdExchange


exchangeManager = {
    'CvmfsDevExchange': CvmfsDevExchange,
    'CvmfsConDBExchange': CvmfsConDBExchange,
    'CvmfsProdExchange': CvmfsProdExchange
}
