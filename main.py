import os

path = '/home/daikinfbn/Brake_Press_Counter4/'

os.system('sudo chown daikinfbn ' + path + 'variables.txt')

with open(path + 'variables.txt','r') as variable_file:
    variables = variable_file.readlines()

while variables[0].split('\n')[0] == 'False':

    os.system('python ' + path + 'Brake_Press_Counter4.py')

    with open(path + 'variables.txt','r') as variable_file:
        variables = variable_file.readlines()

    if variables[1].split('\n')[0] == 'True':
        os.system('sudo git -C ' + path + ' stash')
        os.system('sudo git -C ' + path + ' pull --no-rebase')
        with open(path + 'variables.txt','w') as variable_file:
            variable_file.writelines('False\nFalse')
            
with open( path + 'variables.txt','w') as variable_file:
    variable_file.writelines('False\nFalse')
