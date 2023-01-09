import os

path = '/home/daikinfbn/Brake_Press_Counter4/'

with open(path + 'variables.txt','r') as variable_file:
    variables = variable_file.readlines()

while variables[0].split('\n')[0] == 'False':

    os.system('python ' + path + 'Brake_Press_Counter4.py')

    with open(path + 'variables.txt','r') as variable_file:
        variables = variable_file.readlines()

    if variables[1].split('\n')[0] == 'True':
        os.popen('sudo git stash')
        os.popen('sudo git pull --no-rebase')
        with open(path + 'variables.txt','w') as variable_file:
            variable_file.writelines('False\nFalse')
            
with open( path + 'variables.txt','w') as variable_file:
    variable_file.writelines('False\nFalse')
