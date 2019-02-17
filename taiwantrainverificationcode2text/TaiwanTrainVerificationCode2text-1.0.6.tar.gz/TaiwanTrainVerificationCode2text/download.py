



import urllib.request
import os

PATH = "/".join( os.path.abspath(__file__).split('/')[:-1])

def weight():

    url = 'https://github.com/linsamtw/TaiwanTrainVerificationCode2text/blob/master/cnn_weight/verificatioin_code.h5'  
    os.makedirs('cnn_weight')
    urllib.request.urlretrieve(url, '/{}/{}/verificatioin_code.h5'.format(PATH,'cnn_weight')) 


def ttf():
    
    url = 'https://github.com/linsamtw/TaiwanTrainVerificationCode2text/blob/master/Courier-BoldRegular.ttf'  
    urllib.request.urlretrieve(url, '/{}/Courier-BoldRegular.ttf'.format(PATH)) 

    url = 'https://github.com/linsamtw/TaiwanTrainVerificationCode2text/blob/master/Times%20Bold.ttf'  
    urllib.request.urlretrieve(url, '/{}/Times Bold.ttf'.format(PATH)) 





