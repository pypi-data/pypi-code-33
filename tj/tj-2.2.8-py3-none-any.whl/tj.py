import os, sys, time, shutil, random, base64, hashlib
import os.path
import pyAesCrypt as crypt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import msvcrt as m

__version__="2.2.8"

__doc__='''

 _______ ________
|__   __|___   __| PRODUCTIONS 2018
   | |      | |
   | |    __| |
   |_|    \___/ 


A module that can be used to to multiple common tasks that otherwise you
would do by writing long lines of code

Version: %s

Updated on: 30rd January 7:35 PM
''' % ( __version__)





colors = {"BLACK": [0, 0, 0], "WHITE": [255, 255, 255], "GOLD": [255,223,0], "METALLIC GOLD": [212,175,55], "LIGHT YELLOW": [255, 255, 224],
          "YELLOW": [255, 255, 40], "ORANGE": [255, 165, 0], "DARK ORANGE": [255, 140, 0], "RED": [255, 0, 0],
          "DARK RED": [135, 0, 0], "MAROON": [120, 0, 0], "BROWN": [165, 42, 42], "PINK": [255, 192, 203],
          "HOT PINK": [255, 105, 180], "LIGHT PINK": [255, 182, 193], "VIOLET": [148, 0, 211], "PURPLE": [160, 32, 240],
          "INDIGO": [75, 0, 130], "BLUE": [0, 0, 255], "SKY BLUE": [135, 206, 250], "DARK BLUE": [0, 0, 139],
          "LIGHT GREEN": [0, 200, 0], "GREEN":[50,205,50], "DARK GREEN": [0, 139, 0], "LIME": [0, 255, 0], "FOREST GREEN": [35, 140, 35],
          "GRAY": [128, 128, 128], "CRIMSON": [220, 20, 60], "BRICK": [178, 34, 34], "FUCHSIA": [255, 0, 255],
          "LIGHT GRAY": [211, 211, 211], "SILVER": [92, 192, 192], "DARK GRAY": [105, 105, 105], "OLIVE": [128, 128, 0],
          "TEAL": [0, 128, 128], "CYAN": [0, 255, 255], "CHARCOAL": [54, 70, 80], "CHOCOLATE": [210, 105, 30],
          "WOOD": [255, 165, 79], "FERRARI": [255, 40, 0], "PEACH": [255, 218, 185], "CREAM": [245, 255, 250],
          "GRAPE": [110, 45, 168], "DENIM": [21, 96, 189], "ARMY": [75, 83, 32], "COFFEE": [111, 78, 55],
          "IRON": [203, 205, 205], "COPPER": [184, 115, 51]}

color_names = list(colors.keys())



def transform_color(color1, color2, skipR=1, skipG=1, skipB=1):
    """
transform_color(color1, color2, skipR=1, skipG=1, skipB=1)


This function takes 2 color1 and color2 RGB color arguments, and then returns a
list of colors inbetween the color1 and color2

eg- tj.transform_color([0,0,0],[10,10,20]) returns a list:-
[[0, 0, 0], [1, 1, 1], [2, 2, 2] ... [9, 9, 9], [10, 10, 10], [10, 10, 11] ... [10, 10, 20]]

This function is very useful for creating color fade or color transition effects in pygame.

There are 3 optional arguments, which are skip arguments set to 1 by default.
"""
    L=[] 
    if (color1[0]<color2[0]):i=list(range(color1[0], color2[0]+1, skipR))
    else:i=list(range(color2[0], color1[0]+1, skipR))[::-1]
    if i==[]:i=[color1[0]]
  
    if (color1[1]<color2[1]):j=list(range(color1[1], color2[1]+1, skipG))
    else:j=list(range(color2[1], color1[1]+1, skipG))[::-1]
    if j==[]:j=[color1[1]]

    if (color1[2]<color2[2]):k=list(range(color1[2], color2[2]+1, skipB))
    else:k=list(range(color2[2], color1[2]+1, skipB))[::-1]
    if k==[]:k=[color1[2]]

    x=max(len(i), len(j), len(k))
    for m in range(len(i), x):i+=[i[-1]]
    for m in range(len(j), x):j+=[j[-1]]
    for m in range(len(k), x):k+=[k[-1]]

    for m in range(x):
        l=[i[m], j[m], k[m]]
        L+=[l]
    return L


def allcolors(color=None, flag=False):

    """allcolors(color=None)
If called, this function prints all the colors available in the module
If the optional color argument color is given, it will search colors related
    to the given color.
    eg- allcolors("GRAY") returns "GRAY" , "DARK GRAY", etc.

There is another optional argument called flag.
flag is set to False by default, and it prints the results, and doesn't return
flag=True returns the results in a list, and prints nothing."""
    if color == None:
        L = color_names
    else:
        L = []
        color = color.upper()
        for c in color_names:
            if color in c:
                L += [c]

    if flag == False:
        for i in L: print("%-20s   %s" % (i, colors[i]))
    else:
        return color_names


def get_filename(path):
    """Takes full path of the file as argument
Gives the file name from the full path of the file with extension"""
    path=os.path.abspath(path)
    x=os.path.basename(path)
    return x


def get_foldername(path):
    """Takes a path as a string as argument and returns the name of the folder of the file"""
    #x=os.path.dirname(path)
    path=os.path.abspath(path)
    temp=path.split("\\")
    temp=temp[:-1]
    x="\\".join(temp)
    return x


def get_files_in_folder(path):
    """Takes the full path of a folder as argument
Gives the full path of all the files in a folder in a list"""
    L = []

    for root, dirs, files in os.walk(os.path.abspath(path)):
        for file in files:
            L += [os.path.join(root, file)]
    return L


def factorial(num):
    """Takes a number as argument
Gives factorial of that argument"""
    if num < 0:
        raise "Number is less than 0"
    if type(num) != type(1):
        raise "Number is not an integer"
    r = 1
    for i in range(1, num + 1):
        r = r * i
    return r


def email(email_id, password, recievers, body, subject="Email sent by TJ module Python", attachments=[], email_type='plain', html_resources=[]):
    
    """Args->

    email_id-> The email id of the sender.
    
    password-> The password of email the sender.
    
    recievers-> The list of email id of recievers. recievers argument
    should compulsorily be a list, even if there is just 1 reciever.
    
    body-> The body of the email.
    
    subject-> subject of email.
    
    attachments-> A list of paths of files which you need to send
    as attachment. It is an optional argument.

    email_type-> The type of email text you are going to send. It is set to
    'text' by default, but by setting email_type to 'html', you will be able to
    send beautiful looking emails.In this case, you need to provide the html code
    insetead of any body, i.e. body will contain the html code.

    html_resources-> If your html page contains pictures, then your will have to
    send the path of those pictures in the form of a list. You also have to edit your
    html file such that in all the image tags, src="cid:res<number>", instead of
    writing the pathof the file in the image tag. Also, you need to rename all the
    image files accordingly as res0.png, res1.png, res2.jpg, etc.

    eg.
    HTML code:
    <html>
    .
    .
    <image src="cid:res0" ...>
    .
    .
    . . .<image src="cid:res1"...>
    .
    .
    <image src="cid:res2"...>
    .
    .
    
    <\html>

    and here, html_resources=['images\\res0.png','images\\res1.png','images\\res2.jpg']
    
    # So all the image paths should be replaced by "cid:res<number>" and this
    number should be a proper sequence of 0,1,2,3 and so on. Any error in this part,
    would result into not showing up your image.

    *Also it is adviced to rename the files accordingly to their cid, as shown in the
    above example.
    

    This funtion uses the SMTP library to send an email to the recivers using
    the email id of the sender. It can also send attachments in the email.

    *If you are using Gmail, then you might want to change the settings of your
    email account to allow 3rd party apps to send or recieve emails, or else
    you will not be able to send emails using that email id.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.base import MIMEBase
    from email.mime.image import MIMEImage

    uname = email_id
    pword = password

    emailfrom = email_id
    emailto = recievers

    body = [body]
    subject = subject

    msg = MIMEMultipart()
    msg['From'] = emailfrom
    msg['To'] = ', '.join(emailto)
    msg['Subject'] = subject

    if email_type.upper()=='HTML':
        msg.attach(MIMEText(''.join(body), 'html'))
    else:msg.attach(MIMEText(''.join(body)))

    for i in range(len(html_resources)):
        resource=html_resources[i]
        f=open(resource,'rb')
        data=f.read()
        f.close()
        msgRes = MIMEImage(data)
        msgRes.add_header('Content-ID', f'<res{i}>')
        msg.attach(msgRes)

    ### ATTACH FILES
    for item in attachments:
        part = MIMEBase('application', "zip")

        f = open(item, "rb")
        datatemp = f.read()

        part.set_payload(datatemp)
        filename = get_filename(item)
        part.add_header('Content-Disposition',
                        'attachment; filename="%s"' % filename)
        msg.attach(part)

        ### SECURE CONNECTION
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(uname, pword)

    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()


def is_Folder(path):
    """Takes the path of the folder as argument
Returns is the path is a of a Folder or not in bool"""
    if os.path.isdir(path):return True
    else:return False

def is_File(path):
    """Takes the path of the folder as argument
Returns is the path is a of a Folder or not in bool"""
    if os.path.isfile(path):return True
    else:return False


def get_startup_path():
    """Takes no arguments
Gives a list of full startup paths on a computer
eg:
[
 "C:\\Users\\ABC\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\",
 "C:\\Users\\John PC\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\",
 "C:\\Users\\Monica\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"]

 *[Public, Default ,All Users, Default User] user will not be included in this list
"""

    a = "C:\\Users\\"
    b = "\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\"
    user_L = os.listdir(a)
    L = []
    for user in user_L:
        if user in ['Public', 'Default', 'All Users', 'Default User']:
            continue
        if not is_Folder(a + user):
            continue
        path = a + user + b
        L += [path]
    return L


def convert_bytes(size):
    L = ["Bytes", "KB", "MB", "GB", "TB"]
    for i in range(len(L)):
        if size // (1024 ** i) == 0:
            break
    s = str(size / 1024 ** (i - 1))
    s = s.split(".")
    s1 = s[0]
    s2 = s[1]
    s2 = s2[:2]
    s = s1 + "." + s2
    return "{s} {x}".format(s=s, x=L[i - 1])


def file_size(file_path, Flag=False):
    """file_size(file_path, Flag=False)

Takes the full path of the file as input
Gives the size of the file in bytes

There is another argument Flag (set to False by default).
If Flag is true, it returns in format like 2.3 GB, 5.0 MB, etc.
    """
    size = os.path.getsize(file_path)
    if Flag:
        return convert_bytes(size)
    else:
        return size


def get_last_modified(path,flag=False):
    '''Get the date the the file was last modified of the.
    Arguments:\n path-> the path of the file
    flag-> Its a bool value, when False, the time is returned in
    Epoch seconds, if flag is True, time is returned in proper format.'''
    try:a=os.stat(path)[-2]
    except:raise "Path not found"
    if flag==False:
        return a
    if flag==True:
        return time.asctime(time.localtime(a))



def passed_time(flag=True):
    '''if flag=False, then returns the time after the function is called
        from the time the function was called first time in the program

    if flag=True, then returns the time in seconds b/w two successive calls
    Use it as a generator function
    You can create different instances to use it as per your convinience
    eg-
    import tj
    a=tj.passed_time()
    print(a.next()); time.sleep(5)
    print(a.next()) #This is used after waiting 5 sec.
    b=tj.passed_time()
    print(b.next()); time.sleep(5)
    print(a.next()); time.sleep(5)
    print(b.next())
>>>0.0
>>>5.0
>>>0.0
>>>5.0
>>>10.0
    '''
    t=time.time()
    while True:

        if flag:
            m=time.time()-t
            t=time.time()
            yield m
        if not flag:
            yield time.time()-t


def take_src(name="src.png", DIR=""):
    """Args->
    name-> name of the file with .png or .bmp extension
    DIR-> Folder where you want to save the file
    name="src.py" by default and DIR="" by default (same as working directory)
    Prints and saves the screen shot in .png or .bmp format in a location"""

    try:from autopy import bitmap
    except:raise ModuleNotFoundError("autopy module not found.\nInstall autopy module using 'pip install autopy'")
    
    path=os.path.join(DIR,name)
    bitmap2 = bitmap.capture_screen()
    bitmap2.save(path)


def convert_currency(c1, c2,rate=None, flag=True):
    """Args->
    c1-> This is the currency which will be the input
    c2-> This is the currency which will be the output

    c1 should consist of amount and type in a single string, seperated
        by a space
        eg. '100 EUR' where 100 is the amount and EUR is the type
        
    c2 should only consist of currency only
        eg. 'INR' or 'USD'

        *The purpose of using this string format is to reduce confusion.
        '40 USD' in a single string and 'INR' in another string gives
        clear indication of which currency is being converted in which.
        
    
    rate-> This is the rate of conversion. This argument is set
        to None by default. When rate is None, the rate of conversion
        will be automatically fetched from the internet. When rate is
        provided by the user, that rate will be used instead. The rate
        should be such that c2=c1*rate

    flag-> True by default. If flag is False, all print statements of the
        function will be disabled.

    converts currency c1 to c2 using the currency rate 'rates'. This 'rates'
    Argument will be fetched from the internet automatically from the internet
    or will be provided by the user.

    An example of usage is:
    convert_currency('50 USD', 'INR') would result in 3550INR (taking 1USD = 71INR)

    convert_currency('10 EUR', 'USD', 1.1) would result in 11USD (user gives 1EUR = 1.1USD)"""

    amt1, type1=c1.split(" ")
    amt1=float(amt1)
    type1=type1.upper()
    amt1=round(amt1, 3)
    type2=c2
    type2=type2.upper()

    if rate==None:
        try:from forex_python.converter import CurrencyRates
        except:raise ModuleNotFoundError("forex_python module not found.\nInstall forex_python module using 'pip install forex-python'")

        if flag:print('Fetchig currency exchange rates from internet...\n\n')
        c = CurrencyRates()
        All_rates=c.get_rates(type1)    # All the exchange rates will be based on USD
        rate=All_rates[type2]
        amt2=amt1*rate
        amt2=round(amt2, 3)

        if flag:print(f"{amt1} {type1} equals {amt2} {type2}")

    else:
        amt2=amt1*rate
        amt2=round(amt2, 3)
        if flag:print(f"{amt1} {type1} equals {amt2} {type2}")
    return f'{amt2} {type2}'


def getRandomString(L=None,number=None):
    '''Args->

    L-> optional argument, the function will return a random string of
    characters from the characters provided in the list L. Characters are case-sensitive
    Set to none by default, so any visible characters incluting a-z, A-Z, 0-9 and special
    symbols will be included. Characters from the order 33-126 will be included.

    number-> Length of the string.Set to None by default. When number=None, it will be
    determined randomly in the range 8-20.

    This funtion provides a sting of random characters.

    *make sure you type getRandomCharacters(number=8) if you want to change the
    number of characters instead of getRandomCharacters(8).
    '''
    s=''
    if L==None:
        L=[chr(i) for i in range(33,127)]
    for j in range(number):
        temp=str(random.choice(L))
        s+=temp
    return s
        

def encryptFile(InputFile, OutputFile=None, password=None, delete=False):
    '''Args->

    InputFile-> This is the file which will undergo encryption

    OutputFile-> This is the file you will get after encryption. It
    is an optional argument and set to None by default. When it is None,
    the OutputFile will have the same name an InputFile, and the original
    InputFile will be deleted.

    password-> The password which you will use to encrypt the file. It is an
    optional argument. It is set to None by default, and a passoword
    will be generated randomly consisting of only numbers, of length 8-20.

    delete-> This is an optional argument, set to False by default. If delete=True,
    the original InputFile will be deleted, and you will be left with the OutputFile.
    However, if OutputFile is None, or if OutputFile==InputFile, then it will not delete
    the OutputFile/InputFile.

    This function encrypts a file using AES-256 encryption. It takes a non-encrypted file
    as InputFile and then encrypts it as OutputFile.

    *The buffer-size used for encryption is 32*1024.
'''
    
    tempFile='temp.tjenc'
    
    try:os.remove(tempFile)
    except:pass
    try:os.remove(OutputFile)
    except:pass
    bufferSize=32*1024
    if password==None:
        L=[str(i) for i in range(10)]+[str(i) for i in range(65, 91)]
        password=getRandomString(L=L, number=random.randint(8,20))

    crypt.encryptFile(InputFile, tempFile, password, bufferSize)

    if delete:os.remove(InputFile)

    if (OutputFile==None) or (OutputFile==InputFile):
        OutputFile=InputFile
        os.remove(InputFile)

    os.rename(tempFile, OutputFile)
    return password


def decryptFile(InputFile, password, OutputFile=None, delete=False):
    '''Args->

    InputFile-> This is the file which will undergo decryption, it
    is assumed that InputFile was earlier encrypted with the 'encrypt'
    function of this module.

    password-> The password which you used to encrypt the file.

    OutputFile-> This is the file you will get after decryption. It
    is an optional argument and set to None by default. When it is None,
    the OutputFile will have the same name an InputFile, and the original
    InputFile will be deleted.

    delete-> This is an optional argument, set to False by default. If delete=True,
    the original InputFile will be deleted, and you will be left with the OutputFile.
    However, if OutputFile is None, or if OutputFile==InputFile, then it will not delete
    the OutputFile/InputFile.

    This function decrypts a file encrypted with AES-256 encryption. It takes an encrypted file
    as InputFile and then decrypts it as OutputFile.

    *The buffer-size used for decryption is 32*1024.
'''
    tempFile='temp.tjenc'
    
    try:os.remove(tempFile)
    except:pass
    try:os.remove(OutputFile)
    except:pass
    bufferSize=32*1024

    crypt.decryptFile(InputFile, tempFile, password, bufferSize)

    if delete:os.remove(InputFile)

    if (OutputFile==None) or (OutputFile==InputFile):
        OutputFile=InputFile
        os.remove(InputFile)

    os.rename(tempFile, OutputFile)

        
def delete(path):
    '''Takes a path as an argument
The path can be of a folder or a file.

Autoatically determines wether the path is a file/folder and
is it an empty folder or non-empty folder and then deletes it.'''
    try:shutil.rmtree(path)
    except:
        try:
            os.remove(path)
        except:
            raise FileNotFoundError(path+" file cannot be deleted, it might not exist, or due to no Admin rights")


def __keyGenerator(p):
    '''This funtion is not for use outside this module'''
    password_provided = p
    password = password_provided.encode()   # Convert string to binary string
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'',
        iterations=5000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password)) # Can only use kdf once
    return key

def encrypt(message, password):
    '''Args->

    message-> This is the string which is going to be encrypted

    password-> This the password which you will use for to encryption

    This function is used to easily encrypt strings, using AES encryption.
    
'''
    key=__keyGenerator(password)
    cipher=Fernet(key)
    e_message=cipher.encrypt(message.encode())
    return e_message.decode()


def decrypt(e_message, password):
    '''Args->

    e_message-> This is the encrypted string which is going to be decrypted.
    This string should be encrypted by the encrypt(...) function of this module.

    password-> This the password which you will have used for encryption

    This function is used to easily decrypt strings, which were encrypted by
    the encrypt(...) function of this module.
'''
    key=__keyGenerator(password)
    cipher=Fernet(key)
    d_message=cipher.decrypt(e_message.encode())
    return d_message.decode()


def pinput(prompt='',symbol='*'):
    '''Args->

    prompt-> Like the input() method, pinput also
    accepts a prompt string, which will be displayed
    to the user. It is an optional argument.

    symbol-> This the symbol which will be shown instead
    of characters during typing of password. It is set to
    * by default. You can change it to # or $ or x or even
    an empty string.

    pinput() (pssword-input) is a function, which makes entering
    sensitive data secure, by hiding the characters. This function
    clears the screen, so keep that in mind. And copy pasting of 
    passwords does not work here.
'''
    os.system('cls')
    print(prompt, end='')
    s = ''
    sys.stdout.flush()
    while True:

        c = m.getch()
        if ord(c) == 8:
            os.system('cls')
            print(prompt, end='')
            s = s[:-1]
            print(symbol*len(s), end='')
            sys.stdout.flush()
            continue
        
        c = c.decode()
        sys.stdout.flush()
        if c == '\r':
            break
        s += c
        print('*', end='')
        sys.stdout.flush()
    os.system('cls')
    print(prompt+(symbol*len(s)))
    
    return s


def make_hash(string):
    '''Args->

    string-> This is the string which you want to convert
    to hash.

    This function returns the hash of a string, using SHA256
    algorithm. Returns the hash as a binary string.'''
    
    hash_object = hashlib.sha256(string.encode())
    digest = hash_object.digest()
    return digest


