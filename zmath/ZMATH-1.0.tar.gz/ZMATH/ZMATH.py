version = "1.0"
author = "HusseinA"
purpose = "To make users answer some basic math questions"
prm = ("Mr. Command - Maths".upper())

import random
import time
import os
import getpass
import sys
import math
import platform
os.system("color F0")
#score & question setting
question=0
score=0
from time import sleep
import sys

start=time.time() #captures time upon start of program

def Ttime():
    tf=time.time()
    count=round(tf-start) #adding time to start
    trn=time.strftime("%H:%M:%S", time.gmtime(count))#formatting time values
    print(trn)
    
def logo():                                                                       
    print('  ██████╗     ███╗   ███╗ █████╗ ████████╗██╗  ██╗')   
    print('  ╚══███╔╝     ████╗ ████║██╔══██╗╚══██╔══╝██║  ██║')   
    print('    ███╔╝█████╗██╔████╔██║███████║   ██║   ███████║')   
    print('   ███╔╝ ╚════╝██║╚██╔╝██║██╔══██║   ██║   ██╔══██║')   
    print('  ███████╗     ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║--A {}'.format("HHA"))  
    print('  ╚══════╝     ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝  --v{}'.format(version))
    print('=============================================================')
    

print("ZMATH LOADING...".center(40))
def load():
    for i in range(21): #FPS
        sys.stdout.flush()
        sys.stdout.write('\r') #read output
        # the exact output you're looking for
        sys.stdout.write("%-0s%d%%" % ('\033[47m███\033[0m'*i, 5*i)) #displaying FPS #begins with 0% #multiplied by i value
        sys.stdout.flush() # clears 
        sleep(0.24) #time frames per second
load()
os.system('CLS')#clears sceen

correct="+1 mark!"
effort="+0.5 mark"

root="root"
end="{}\033[0m" #prevent color takeover

r00t="root","Root","ROOT", "", " " # default

logo()
#loop
while True:
    roots=input("Username: ")
    if roots in r00t :
        break
    elif roots in roots:
        del root
        root=roots
        break
    else:
        print("Error")

def Super():
    global root
    del root #delete variable
    root=input("Enter name: \033[98m \033[0m") #renew variable
    
def helper():
    print('Helpsheet for ZMATH. \nThis program works by commands.',
          '\n-------------------------------------------------------------------------------------------------------------',
          '\n \033[01m Here are a list of the commands to help you use this program. \033[0m',
          '\n-------------------------------------------------------------------------------------------------------------',
          '\n+ : This command gives you addition questions',
          '\n- : This command gives you subtraction questions',
          '\n* : This command gives you multiplication questions',
          '\n/ : This command gives you division questions',
          '\n% : This command gives you percentage questions',
          '\nr : This command marks your questions',
          '\na : This command gives you Algebra questions',
          '\nf : This command gives you financial questions',
          '\np : This command gives you probability questions',
          '\nt : This command shows time spent',
          '\nc : This command clears the terminal',
          '\ntrig : This command gives you pythogoras questions',
          '\ntrig : This command gives you trigonmetry questions',
          '\nroot : This command changes the terminal name',
          '\nexit : This command exits the terminal',
          '\n-------------------------------------------------------------------------------------------------------------')
def info():
    mes=("\n************************************************ \nZMATH -v{} \nAuthor: {} \nPurpose: {} \nI hope you enjoy using this\n************************************************".format(version,author,purpose))
    print(mes.rjust(25,'*'))

#--------------------------------------------------Addition/add/plus#-----------------------------------------
def aq():
    global question
    global score
    question+= 1
    n1=random.randint(1,1000)
    n2=random.randint(1,1000)
    q=("\033[34mQuestion {}.    What is {}+{}=".format(question,n1,n2))
    print(q)

    while True:
        try:
            ua=(input("\033[90m Answer:       \033[0m"))
            ca=(n1+n2)

            if int(ua)==ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0m The correct answer was {}\033[0m".format(ca))
                break
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return aq()
#--------------------------------------------------pythogoras#------------------------------------
def pythogoras():
    global question
    global score
    global ga

    question+= 1
    sohcahtoa="Hypothenuse","Opposite","Adjacent"
    angle="Hypothenuse","Opposite","Adjacent"
    a2=random.choice(angle)
    sideA=random.choice(sohcahtoa)
    
    n1=random.randint(20,40) #angle degree
    n2=random.randint(4,18) #missing value of opposite or adjacent

    if sideA == "Adjacent": #soh - opposite/hypotenuse
        find="Hypotenuse","Opposite" # find the missing side
        sideB=random.choice(find)
        
    elif sideA=="Opposite": #cah - adjacent/hyptenuse
        find="Adjacent","Hypotenuse"
        sideB=random.choice(find)

    elif sideA=="Hypthenuse": #toa - opposite/adjacent
        find="Opposite","Adjacent"
        sideB=random.choice(find)
        
    if sideA =="Adjacent" and sideB== "Opposite" : #given angle
        sideC="Hypotenuse" #ga value
        cai=math.sqrt(n1**2+n2**2)
        
    elif sideA =="Adjacent" and sideB== "Hypotenuse":
        sideC="Opposite"
        cai=math.sqrt(n1**2-n2**2)
        
    elif sideA =="Opposite" and sideB== "Adjacent":
        sideC="Hypotenuse"
        cai=math.sqrt(n1**2+n2**2)
        
    elif sideA =="Opposite" and sideB== "Hypotenuse":
        sideC="Adjacent"
        cai=math.sqrt(n1**2-n2**2)
        
    elif sideA =="Hypthenuse" and sideB== "Opposite":
        sideC="Adjacent"
        cai=math.sqrt(n1**2-n2**2)
        
    elif sideA =="Hypthenuse" and sideB == "Adjacent":
        sideC="Opposite"
        cai=math.sqrt(n1**2-n2**2)
    
    q=("Question {}.    A right angle triangle has an {} of {}cm & {} value of {}cm. \n               Workout the length of {}. Answer should be in 2dp".format(question,sideA,n2,sideB,n1,sideC))
    print(q) #displaying the question

    while True:
        try:
            ca = round(cai,2)
            ua=(input("\033[90mAnswer:        \033[0m")) #user answer

            if float(ua) in (ca,round(ca),round(ca,1),round(ca,2),('{:.2f}'.format(ca)),('{:.1f}'.format(ca))):
                score+=1 #score counter
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0m The {} was {}cm".format(sideC,ca))
                break
        except ValueError:
            question-=1 #if error. reset score
            print("Invalid answer. Try again")
            return trigonmetry() #offer new question if error
#--------------------------------------------------financial#-----------------------------------------
def f():
    global question
    global score
    question+= 1
    names="Ellison","Brin","Gates","Torvalds","Bezos","Zuckerburg","Musk","Page"
    chosen=random.choice(names)
    n1=random.uniform(4.5,60.6) #random float generator
    m1=round(n1,2)
    q=("\033[34mQuestion {}.    If {} makes ${} per second. How much will {} earn in a year?".format(question,chosen,m1,chosen))
    print(q)

    while True:
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            cas=float(m1*86400*365)
            ca=round(cas,2)

            if float(ua) in (ca, int(ca),round(ca),round(ca,2),round(ca,1)):
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0mThe correct answer was ${0:.2f}\033[0m".format(round(ca,2)))
                break
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return f()
#--------------------------------------------------trigonmetry#-----------------------------------------
def trigonmetry():
    global question
    global score
    global ga

    question+= 1
    sohcahtoa="Sin","Cosin","Tan"
    angle="Hypothenuse","Opposite","Adjacent"
    a2=random.choice(angle)
    chosen=random.choice(sohcahtoa)

    if chosen == "Sin": #soh - opposite/hypotenuse
        find="Hypotenuse","Opposite" # find the missing side
        ga=random.choice(find)
        n1=random.randint(20,80) #angle degree value
        n2=random.randint(1,20) #missing value of adjacent or opposite
        
    elif chosen=="Cosin": #cah - adjacent/hyptenuse
        find="Adjacent","Hypotenuse"
        ga=random.choice(find)
        n1=random.randint(20,80) #angle degree
        n2=random.randint(1,20) #missing value of adjacent or hypotenuse
    elif chosen=="Tan": #toa - opposite/adjacent
        find="Opposite","Adjacent"
        ga=random.choice(find)
        n1=random.randint(20,80) #angle degree
        n2=random.randint(1,20) #missing value of opposite or adjacent
        
    if chosen =="Sin" and ga== "Opposite": #given angle
        ant="Hypotenuse" #ga value
        cai=(n2 / (math.sin(math.radians(n1))))
        
    elif chosen =="Sin" and ga== "Hypotenuse":
        ant="Opposite"
        cai=(n2 * (math.sin(math.radians(n1))))
        
    elif chosen =="Cosin" and ga== "Adjacent":
        ant="Hypotenuse"
        cai = (n2 / (math.cos(math.radians(n1))))
        
    elif chosen =="Cosin" and ga== "Hypotenuse":
        ant="Adjacent"
        cai = (n2 * (math.cos(math.radians(n1))))
        
    elif chosen =="Tan" and ga== "Opposite":
        ant="Adjacent"
        cai = (n2 / (math.tan(math.radians(n1))))
        
    elif chosen =="Tan" and ga == "Adjacent":
        ant="Opposite"
        cai = (n2 * (math.tan(math.radians(n1))))
    else:
        print("Sys error 404")
    q=("Question {}.    A right angle triangle has an angle of {}° degrees & {} value of {}cm. \n               Workout the length of {}. Answer should be in 2dp".format(question,n1,ga,n2,ant))
    print(q) #displaying the question

    while True:
        try:
            ca = round(cai,2)
            ua=(input("\033[90mAnswer:        \033[0m")) #user answer #user answer

            if float(ua)==(round(ca,2)):
                score+=1 #score counter
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0m The {} was {}cm".format(ant,ca))
                break
        except ValueError:
            question-=1 #if error. reset score
            print("Invalid answer. Try again")
            return trigonmetry() #offer new question if error

#------------------------------/probability#---------------------------------
def probability():
    global question
    global score
    question+= 1
    ldn=random.randint(80,500)#percentage amount
    yrk=random.randint(80,500)#% value
    knt=random.randint(80,500)#% value
    city=("Kent","London","York")
    chosen = random.choice(city)

    prob=ldn+yrk+knt
    print(chosen)
    print("\033[34mQuestion {}.    A lotto is chosen at random.There are {} participants from London. {} from York. {} from Kent. \n               Predict how many people from {} will win the lotto?".format(question,ldn,yrk,knt,chosen))
    while True:
        try:
            prob=(ldn+yrk+knt)
            ua=(input("\033[90mAnswer:        \033[0m"))
            if chosen=="London":
                ca=int(prob/ldn)
            elif chosen=="Kent":
                ca =int(prob/knt)
            elif chosen == "York":
                ca=int(prob/yrk)
                
            if int(ua) == ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break # break the loop
            else:
                print("\33[101mWrong!\033[0mThe correct answer was {} from {} will probably win\033[0m".format(int(ca),chosen))
                break #break the 
        except ValueError:
            print("Invalid answer. Try again")
            return probability()
#------------------------------/percentage/percent/%/out of 100#---------------------------------
def percentage():
    global question
    global score
    question+= 1
    n1=random.randint(1,100)#percentage amount
    n2=random.randint(1,1000)#% value
    print("\033[34mQuestion {}.    What is {}% of {} ?".format(question,n1,n2))
    while True:
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            ca=(n2/100*n1)
            aca=round(ca),round(ca,2),round(ca,-1)
            
            if float(ua) == ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            elif float(ua) in aca:
                score+=0.5
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0m The correct answer was {}\033[0m".format(round(ca,2)))
                break
        except ValueError:
            print("Invalid answer. Try again")
            return percentage()
#------------------------------/Ratio---------------------------------
def ratio():
    global question
    global score
    question+= 1
    a=random.randint(1,10)#alice ratio
    b=random.randint(1,10)# bob ratio
    s=random.randint(1,10) #Shiraz ratio
    money = random.randint(60,1000) #sweets
    tratio = a+b+s
    da= (money/tratio)
    ca=da*s
    print("\033[34mQuestion {}.     Alice, Bob and Shiraz are going to share £{} in {}:{}:{} \n               How much does Shiraz get?".format(question,money,a,b,s))
    while True:
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            aca=round(ca),round(ca,-1),round(ca,2)
        
            if float(ua) == ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            elif float(ua) in aca:
                score+=0.5
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0m The correct answer was £{} \033[0m".format(round(ca,2)))
                break
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return ratio()

#------------------------------/Algebra---------------------------------
def Algebra():
    global question
    global score
    question+= 1
    n1=random.randint(1,10)#cost mph
    n2=random.randint(100,1000)# overall
    ff=random.randint(10,30) #fixed fare
    print("\033[34mQuestion {}.    (m x {})+f=c m=mile f=fixed fare c=cost.\n               if cost was £{} & ff was £{}. State amount of miles covered.".format(question,n1,n2,ff))
    while True:
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            ca= (n2-ff)/n1
            aca=round(ca),round(ca,2),round(ca,-1)
            
            if float(ua) == ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            elif float(ua) in aca:
                score+=0.5
                print("\033[33m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0mThe correct answer was {} miles\033[0m".format(round(ca,2)))
                break
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return Algebra()
def Algebra2():
    global question
    global score
    question+= 1
    n1=random.randint(3,20)#cost mph
    m=random.randint(10,100)# overall miles
    f=random.randint(10,100) #fixed fare
    print("\033[34mQuestion {}.    (m x £{})+f=c m=mile f=fixed fare c=cost. \n               if Milage was {} miles & ff was £{}. State Total costs.".format(question,n1,m,f))
    while True:
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            ca= (m*n1)+f
            aca=round(ca),round(ca,2),round(ca,-1)

            if float(ua) == ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
            elif float(ua) in aca:
                score+=0.5
                print("\033[33m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0m The correct answer was £{}\033[0m".format(round(ca,2)))
                break
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return Algebra2()
#------------------------------/subtraction/minus/take-away/takeaway#---------------------------------
def sq():
    global question
    global score
    question+= 1
    n1=random.randint(100,1000)
    n2=random.randint(1,250)
    print("\033[34mQuestion {}.    What is {}-{}=".format(question,n1,n2))
    while True:
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            ca=(n1-n2)
            if int(ua)==ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            else:
                print("\33[101mWrong!\033[0m The correct answer was {}\033[0m".format(ca))
                break
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return sq()
#-------------/multiply/times/multipication#---------------------------------------------------
def mq():
    global question
    global score
    question+= 1
    n1=random.randint(1,1000)
    n2=random.randint(1,10)
    print("Question {}.    What is {}x{}=".format(question,n1,n2))
    while True:
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            ca=(n1*n2)
            TA=round(ca,0),round(ca,-1)
                
            if int(ua)==ca:
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
                
            elif int(ua) in TA:
                score+=0.5
                print(effort.lower())
                break
            else:
                print("\33[101mWrong!\033[0m The correct answer was {}\033[0m".format(ca))
                break
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return mq()
#-------------/division/divide/divide by#---------------------------------------------------
def dq():
    global question
    global score
    question+= 1
    n1=random.randint(10,1000)
    n2=random.randint(1,10)
    print("\033[34mQuestion {}.    what is {}÷{}=\033[0m".format(question,n1,n2))
    while True: #starting a loop
        try:
            ua=(input("\033[90mAnswer:        \033[0m"))
            ca=(n1/n2)
            TA = round(ca,1),round(ca,2),round(ca)
            
            if isinstance(ca,int) and int(ua)==ca:#integer correct answers
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            elif isinstance (ca,float) and float(ua)== ca: #float correct answers
                score+=1
                print("\033[42m {}\033[0m".format(correct.upper()))
                break
            elif isinstance (ca,float) and float(ua) in TA: #float half mark
                score+=0.5
                print(effort.lower())
                nreak
            elif isinstance (ca,int) and int(ua) in TA: #int half mark
                score+=0.5
                print(effort.lower())
                break
            else:
                print("\33[101mWrong!\033[0m The correct answer was {}".format(ca,))
                break #break the loop
        except ValueError:
            question-=1
            print("Invalid answer. Try again")
            return dq() #triggering question again

#commands trigger
ac= "add" , "plus" , "+" , "addition" 
sc= "subtract" , "take away" , "take-away" , "-" , "minus" 
mc= "multiply" , "times" , "x" , "*" , "multiplication" 
dc= "divide" , "division" , "/" , "d"
closer= "quit","exit", "shutdown"
exm= "Results","result","r","grade","mark"
prc="Percentage","%","percent"
error = "","\n"," ",
helps="help","helpsheet","helper","helps","h"
clear="C","CLEAN","CLEAR"
#questions/answers/

def request():
    os.system('CLS')#clears sceen
    logo()
    print("\033[07m \033[30mWelcome {}. What are your commands? \033[0m".format(root))


request()
while True:
    command = input("\033[32m{}@{}-V{}:\033[0m \033[01m \033[34m~ \033[0m#>> \033[0m".format(root,platform.system(),platform.release()))
    if command in ac:
        aq()
    elif command in sc  :
        sq()
    elif command in mc :
        mq()
    elif command in dc:
        dq()
    elif command in prc:
        percentage()
    elif command in exm and question == 0:
        print("Result is impossible without answering some questions")
    elif command in exm:
        print("----------------------------------------------------------------------------")
        print("\33[32mTest Marks\033[0m | {} out of {}  ".format(score, question))
        print("\33[32mPercentage\033[0m |",int(score/question*100),"%         ")
        print("----------------------------------------------------------------------------")
    elif command == "save" and score == 0:
        print("Save is impossible without completing answers")
    elif command == "save":
        name = str(input("Enter name: "))
        file = open("Score.txt","a+")
        file.write("\nName:  {} - Score: {} out of {}".format(name,score,question))
        file.close()
    elif command in closer:
        print("Are you sure you wish to exit?")
        
        break
    elif command.upper() in clear:
        os.system('CLS')#clears sceen
        logo()
        request()
    elif command =="root":
        Super()
    elif command == "info":
        info()
    elif command in helps:
        helper()
    elif command in ("a1","A2","a","A"):
        cho=(Algebra(),Algebra2())
        random.choice(cho)
    elif command in ("Ratio","ratio"):
        ratio()
    elif command in ("Time","time","tt","t"):
        Ttime()
    elif command in ("probability","predict","p"):
        probability()
    elif command in ("trig","Trigonmetry"):
        trigonmetry()
    elif command in ('f','financial','Arithmetic',"Financial math"):
        f()
    elif command in ("pythogoras","py"):
        pythogoras()
    else:
        print("Invalid Command. TYPE '{}' FOR HELP".format('h'.lower()))



