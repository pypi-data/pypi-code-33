import RPi.GPIO as GPIO
import time

PIN = 26
GPIO.setmode(GPIO.BCM)  
GPIO.setup(PIN,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(12, GPIO.OUT)

def signal_recive():
    if GPIO.input(PIN) == 0:  
        count = 0  
        while GPIO.input(PIN) == 0 and count < 200:  
            count += 1  
            time.sleep(0.00006)  

        count = 0  
        while GPIO.input(PIN) == 1 and count < 80:  
            count += 1  
            time.sleep(0.00006)  

        idx = 0  
        cnt = 0  
        data = [0,0,0,0]  
        for i in range(0,32):  
            count = 0  
            while GPIO.input(PIN) == 0 and count < 15:  
                count += 1  
                time.sleep(0.00006)  

            count = 0  
            while GPIO.input(PIN) == 1 and count < 40:  
                count += 1  
                time.sleep(0.00006)

            if count > 8:  
                data[idx] |= 1<<cnt  
            if cnt == 7:  
                cnt = 0  
                idx += 1  
            else:  
                cnt += 1  
        if data[0]+data[1] == 0xFF and data[2]+data[3] == 0xFF:  
             print("Get the key: 0x%02x" %data[2])  
             return data[2]
        return 0x00