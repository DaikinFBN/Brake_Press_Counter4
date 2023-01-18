import os
import Brake_Press_Counter4 as bpc
import secrets
import RPi.GPIO as GPIO

os.system('sudo chown daikinfbn ' + bpc.path + 'variables.txt')
# check to see if settings text file exist and copy variable text data into it if it doesn't exist
if not os.path.isfile(bpc.path+'settings.txt'):
    with open('variables.txt','r') as variable_file:
        variable_data = variable_file.readlines()
    with open('settings.txt','w') as settings_file:
        settings_file.writelines(variable_data)
os.system('sudo chown daikinfbn ' + bpc.path + 'settings.txt')

while bpc.read_txt([1])[0] == 'False':

    bpc.CounterDisplay()
    GPIO.cleanup()
    if bpc.read_txt([2])[0] == 'True':

        os.system('sudo git -C ' + bpc.path + ' stash')
        os.system('sudo git -C ' + bpc.path + ' pull https://DaikinFBN:' + secrets.get('GIT_TOKEN') + '@github.com/DaikinFBN/Brake_Press_Counter4.git --no-rebase')
        os.system('sudo chown daikinfbn ' + bpc.path + 'variables.txt')
        os.system('sudo chown daikinfbn ' + bpc.path + 'settings.txt')

bpc.write_txt([1],['False'])
