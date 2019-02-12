import smtplib
def send(fr,to,password,content):
    try:
        mail=smtplib.SMTP('smtp.gmail.com',587)
        mail.ehlo()
        mail.starttls()
        mail.login(fr,password)
        mail.sendmail(fr,se,content)
        mail.close()
    except:
        print("Errror: permission denied from gmail. please give permission from gmail")
