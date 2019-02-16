import subprocess

def send_notification(table):
    text = """ "MeylenPlan" "$(echo " \n"""

    if table is not None:
        text += table
    else:
        text += "Ich habe heute leider kein Essen für dich."

    text+=""" ")" """

    bash = 'notify-send ' + text
    subprocess.Popen(bash,shell=True)

