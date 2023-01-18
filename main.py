import os

import secrets
import RPi.GPIO as GPIO

path = '/home/daikinfbn/Brake_Press_Counter4/'

os.system('sudo chown daikinfbn ' + path)
# check to see if settings text file exist and copy variable text data into it if it doesn't exist
if not os.path.isfile(path+'settings.txt'):
    with open(path+'variables.txt','r') as variable_file:
        variable_data = variable_file.readlines()
    with open(path+'settings.txt','w') as settings_file:
        settings_file.writelines(variable_data)
os.system('sudo chown daikinfbn ' + path + 'settings.txt')

import Brake_Press_Counter4 as bpc

while bpc.read_txt([1])[0] == 'False':

    bpc.CounterDisplay()
    GPIO.cleanup()
    if bpc.read_txt([2])[0] == 'True':

        os.system('sudo git -C ' + path + ' stash')
        os.system('sudo git -C ' + path + ' pull https://DaikinFBN:' + secrets.secrets.get('GIT_TOKEN') + '@github.com/DaikinFBN/Brake_Press_Counter4.git --no-rebase')
        os.system('sudo chown daikinfbn ' + path + 'variables.txt')
        os.system('sudo chown daikinfbn ' + path + 'settings.txt')

bpc.write_txt([1],['False'])
