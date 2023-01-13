import os
import Brake_Press_Counter4 as bpc
import secrets
import RPi.GPIO as GPIO



os.system('sudo chown daikinfbn ' + path + 'variables.txt')

while bpc.read_txt([1])[0] == 'False':

    bpc.CounterDisplay()

    if bpc.read_txt([2])[0] == 'True':

        os.system('sudo git -C ' + path + ' stash')
        os.system('sudo git -C ' + path + ' pull https://DaikinFBN:' + secrets.get('GIT_TOKEN') + '@github.com/DaikinFBN/Brake_Press_Counter4.git --no-rebase')
        os.system('sudo chown daikinfbn ' + path + 'variables.txt')

        bpc.write_txt([2],['False'])

bpc.write_txt([1],['False'])

GPIO.cleanup()
