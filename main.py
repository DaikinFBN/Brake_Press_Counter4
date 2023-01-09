import os

with open('variables.txt','w') as variable_file:
    variable_file.writelines('False\nFalse')

with open('variables.txt','r') as variable_file:
    variables = variable_file.readlines()

while variables[0].split('\n')[0] == 'False':

    os.system('python Brake_Press_Counter4.py')

    with open('variables.txt','r') as variable_file:
        variables = variable_file.readlines()

    if variables[1].split('\n')[0] == 'True':
        os.popen('sudo git stash')
        os.popen('sudo git pull --no-rebase')
        with open('variables.txt','w') as variable_file:
            variable_file.writelines('False\nFalse')
