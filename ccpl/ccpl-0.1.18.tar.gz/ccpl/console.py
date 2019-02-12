import os

testtext = "Spam, eggs and bacon good sir!"

def clear():
    os.system('cls')

def prints(text=testtext):
    print('\r'+str(text), end="")

def printc(text=testtext):
    clear()
    print(text)

if __name__ == '__main__':
    prints("This is the CCPL console module. For help on CCPL, run ccpl.help")