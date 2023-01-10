# Version 4.2

import tkinter as tk
from PIL import ImageTk, Image
from time import strftime
from datetime import datetime
import RPi.GPIO as GPIO
import os
from secrets import secrets

# user defined variables
change_percents = [75,90] # less than 75 is red 75-90 is yellow and 90 and above is green
loop_time = 5 #ms
blink_time = 500 #ms  must be a multipule of loop_time!
auto_reset_times = ['7:00'] # counter resets automatically at these times, first time will also reset yesterdays saved values to revent cheating
shift_times = [['8:00','16:30'],['17:00','21:00']]  # first shift start and end time and then second shift start and end time Currntly second shift auto start is disabled
count_pin = 11 #IO17 on terminal block
wait_time = .1 # seconds 
path = '/home/daikinfbn/Brake_Press_Counter4/' # path to the git folder

# appearance setting
bgcolors = ['#1e1e1e','#252526','#333333','#37373d'] # background colors
idcolors = ['red','yellow','green'] # identification colors that change based on the goal
font_color = ['#ffffff','black']
fonts = ['Helvetica 36 bold','Helvetica 124 bold','Helvetica 24'] #top text , middle text, bottom text

# counters
past_index = 0
prev_loop_time = 0
past_values = [[0,0],[0,0],[0,0]] # [bendcount , shift goal]  store a few past values incase of accidental resets

# used to prevent cheaing and stop signal noise
risen = True
fallen = False
can_count = True
last_rise = datetime.now()
last_fall = datetime.now()
press_time = last_fall - last_rise

# redefine shift_time start and end times as datetime object
shift_times[0][0] = datetime.now().replace(hour=int(shift_times[0][0].split(':')[0]),minute=int(shift_times[0][0].split(':')[1]))
shift_times[0][1] = datetime.now().replace(hour=int(shift_times[0][1].split(':')[0]),minute=int(shift_times[0][1].split(':')[1]))
shift_times[1][0] = datetime.now().replace(hour=int(shift_times[1][0].split(':')[0]),minute=int(shift_times[1][0].split(':')[1]))
shift_times[1][1] = datetime.now().replace(hour=int(shift_times[1][1].split(':')[0]),minute=int(shift_times[1][1].split(':')[1]))

# initalize the RPi GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(count_pin,GPIO.IN)

#defining fuctions
def increase_count(event):
    global risen,fallen,last_rise,wait_time,last_fall,press_time,can_count#,current_fall,current_rise
    
    if GPIO.input(count_pin) == 0 and fallen == False:
        fallen = True
        risen = False
        can_count = True
        last_fall = datetime.now()
        
    if  GPIO.input(count_pin) == 1 and risen == False:
        risen = True
        fallen = False
        last_rise = datetime.now()
        press_time =  (last_fall - last_rise) * -1
    
    if press_time.total_seconds() > wait_time and fallen == False and can_count == True:
        can_count = False
        count = int(bend_count.cget('text'))
        count += 1
        bend_count['text'] = str(count)

def interact_widget(event):
    global past_index
    if frame_btm.focus_get() == input_goal_entry and not input_goal_entry.get() == "":
        shift_goal['text'] = input_goal_entry.get()
        input_goal_entry.delete(0, tk.END)

    if frame_btm.focus_get() == resetbtn and not shift_goal.cget("text") == "0":
        past_values.append([int(bend_count.cget("text")),int(shift_goal.cget("text"))])
        past_values.pop(0)
        shift_goal['text'] = "0"
        bend_count['text'] = "0"
        input_goal_entry.focus_set()
        input_goal_entry['bg'] = bgcolors[3]
        resetbtn['bg'] = bgcolors[1]

    if frame_btm.focus_get() == undobtn:
        if past_index  == 0:
            past_index = 2
        else:
            past_index -= 1
        shift_goal['text'] = str(past_values[past_index][1])
        bend_count['text'] = str(past_values[past_index][0])
             

    
def loop():  # main update loop
    global prev_loop_time, blink_time, past_values
    time.config(text=strftime('%H:%M:%S %p'))  #update clock text

    if shift_goal.cget("text") == "0" and prev_loop_time == blink_time: # blink red
        change_color(font_color[1],idcolors[0])
    elif shift_goal.cget("text") == "0" and prev_loop_time == (blink_time*2): # blink to background color
        change_color(font_color[0],bgcolors[0])
    elif int(bend_count.cget("text")) < (int(current_goal.cget('text'))*(change_percents[0]/100)) and not shift_goal.cget("text") == "0": # change to yellow when bend count is less than goal
        change_color(font_color[1],idcolors[0]) 
    elif int(bend_count.cget("text")) >= (int(current_goal.cget('text'))*(change_percents[0]/100)) and int(bend_count.cget("text")) < (int(current_goal.cget('text'))*(change_percents[1]/100)) and not shift_goal.cget("text") == "0": # change to yellow when bend count is less than goal
        change_color(font_color[1],idcolors[1])      
    elif int(bend_count.cget("text")) >= (int(current_goal.cget('text'))*(change_percents[1]/100)) and not shift_goal.cget("text") == "0": # change to green when bend count is greater than goal
        change_color(font_color[1],idcolors[2])

    if prev_loop_time == 1000: # for the blinking red
        prev_loop_time = 0
    else:
        prev_loop_time += loop_time

    for t in auto_reset_times: #  times when the bend count and shift goal reset to zero
        if t == strftime('%H:%M'):
            shift_goal['text'] = "0"
            bend_count['text'] = "0"
  
    if auto_reset_times[0] == strftime('%H:%M'): # reset past_values to prevent reuse from previous days bend counts
        past_values = [[0,0],[0,0],[0,0]]

    if current_goal.cget("text") != "0": # update efficiency
        efficiency['text'] = str(round(int(bend_count.cget("text")) * 100 / int(current_goal.cget('text')))) + '%'

    if datetime.now() > shift_times[0][0] and datetime.now() < shift_times[0][1]:  # update current_goal for first shift
        shift_percent = datetime.now()-shift_times[0][0]
        shift_total = shift_times[0][1] - shift_times[0][0]
        current_goal['text'] = str(round((shift_percent / shift_total)*int(shift_goal.cget('text'))))

#    elif datetime.now() > shift_times[1][0] and datetime.now() < shift_times[1][1]: # update current_goal for second shift
#        shift_percent = datetime.now()-shift_times[1][0]
#        shift_total = shift_times[1][1] - shift_times[1][0]
#        current_goal['text'] = str(round((shift_percent / shift_total)*int(shift_goal.cget('text'))))
    win.after(loop_time,loop)

def manual_bend_count(event):  #manually increase to bend count by one used for testing
    count = int(bend_count.cget('text'))
    count += 1
    bend_count['text'] = str(count)

def manual_goal_count(event):  #manually increase to goal count by one used for testing
    count = int(current_goal.cget('text'))
    count += 1
    current_goal['text'] = str(count)
    
def change_color(fg,bg):
    if bend_count['bg'] == bg:
        pass
    else:
        bend_count['bg'] = bg
        bend_count['fg'] = fg
        current_goal['bg'] = bg
        current_goal['fg'] = fg
        shift_goal['bg'] = bg
        shift_goal['fg'] = fg
        efficiency['bg'] = bg
        efficiency['fg'] = fg
    
def change_focus_right(event):
    event.widget.tk_focusNext().focus()

    if frame_btm.focus_get() == input_goal_entry:
        input_goal_entry['bg'] = bgcolors[3]
        undobtn['bg'] = bgcolors[1]

    if frame_btm.focus_get() == resetbtn:
        resetbtn['bg'] = bgcolors[3]
        input_goal_entry['bg'] = bgcolors[1]

    if frame_btm.focus_get() == undobtn:
        undobtn['bg'] = bgcolors[3]
        resetbtn['bg'] = bgcolors[1]

    return("break")

def change_focus_left(event):
    event.widget.tk_focusPrev().focus()

    if frame_btm.focus_get() == input_goal_entry:
        input_goal_entry['bg'] = bgcolors[3]
        resetbtn['bg'] = bgcolors[1]

    if frame_btm.focus_get() == resetbtn:
        resetbtn['bg'] = bgcolors[3]
        undobtn['bg'] = bgcolors[1]

    if frame_btm.focus_get() == undobtn:
        undobtn['bg'] = bgcolors[3]
        input_goal_entry['bg'] = bgcolors[1]

    return("break")

def test_val(inStr,acttyp,index): #Restricts the entry box to numbers and 4 charactures max

    if acttyp == '1': #insert
        if not inStr.isdigit() or int(index) >3:
            return False
    return True

def close_window(event): # close the window
    with open(path + 'variables.txt','w') as variable_file:
        variable_file.writelines('True\nFalse')
    win.destroy()
    
    
def update_window(event):
    os.popen('sudo git -C ' + path + ' fetch https://DaikinFBN:' + secrets.get('GIT_TOKEN') + '@github.com/DaikinFBN/Brake_Press_Counter4.git')
    update_status = os.popen('sudo git -C ' + path + ' status https://DaikinFBN:' + secrets.get('GIT_TOKEN') + '@github.com/DaikinFBN/Brake_Press_Counter4.git').read()
    if update_status.split('\n')[1] != "Your branch is up to date with 'origin/main'.":
        with open(path + 'variables.txt','w') as variable_file:
            variable_file.writelines('False\nTrue')
        win.destroy()
    else:
        with open(path + 'variables.txt','w') as variable_file:
            variable_file.writelines('False\nFalse')
        pass

#make the gui object
win = tk.Tk()

#key binding
win.bind('<KP_Multiply>', change_focus_right)
win.bind('<KP_Divide>', change_focus_left)
win.bind('<Control-w>',close_window)
win.bind('<Control-u>',update_window)
win.bind('<KP_Subtract>',update_window)
win.bind('<KP_Enter>',interact_widget)
win.bind('<Return>',interact_widget)
win.bind('<b>',manual_bend_count)
win.bind('<g>',manual_goal_count)

#configure window grids for frames
#win.attributes('-fullscreen',True)
win.geometry("1360x768")
win_height = win.winfo_screenheight()
win_width = win.winfo_screenwidth()
win.grid_columnconfigure(0,weight=1)
win.grid_rowconfigure(0,weight=1)
win.grid_rowconfigure(1,weight=8)
win.grid_rowconfigure(2,weight=1)

#Make frames
frame_top = tk.Frame(win,bg = bgcolors[1])
frame_top.grid(row=0,column=0,sticky='nesw')
frame_top.grid_columnconfigure(0,weight=1)
frame_top.grid_columnconfigure(1,weight=2)
frame_top.grid_columnconfigure(2,weight=1)
frame_top.grid_rowconfigure(0,weight=1)

frame_mid = tk.Frame(win,bg = bgcolors[0])
frame_mid.grid(row=1,column=0,sticky='nesw')
frame_mid.grid_rowconfigure(0,weight=1)
frame_mid.grid_rowconfigure(1,weight=1)
frame_mid.grid_rowconfigure(2,weight=1)
frame_mid.grid_rowconfigure(3,weight=1)
frame_mid.grid_columnconfigure(0,weight=1)
frame_mid.grid_columnconfigure(1,weight=3)

frame_btm = tk.Frame(win,bg = bgcolors[1])
frame_btm.grid(row=2,column=0,sticky='nesw')
frame_btm.grid_rowconfigure(0,weight=1)
frame_btm.grid_columnconfigure(0,weight=1)
frame_btm.grid_columnconfigure(1,weight=1)
frame_btm.grid_columnconfigure(2,weight=1)
frame_btm.grid_columnconfigure(3,weight=1)

#Defineing top frame widgets
img = Image.open(path + "daikin_logo2.PNG")
resized_image= img.resize((203,43), Image.ANTIALIAS)
new_image= ImageTk.PhotoImage(resized_image)
daikin_label = tk.Canvas(frame_top,height=50,width=240,bg=bgcolors[1],highlightbackground=bgcolors[1])
daikin_label.grid(row=0,column=0,sticky='nswe')
daikin_label.create_image(10,25,anchor=tk.W,image=new_image)

machine = tk.Label(frame_top,text='EPE',font=fonts[0],fg=font_color[0],bg=bgcolors[1])
machine.grid(row=0,column=1,sticky='news')

time = tk.Label(frame_top,text='',font=fonts[0],fg=font_color[0],bg=bgcolors[1])
time.grid(row=0,column=2,sticky='nes')

#defining middle frame widgets
bend_count_label = tk.Label(frame_mid,text='Bend Count',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
bend_count_label.grid(row=0,column=0,sticky='nsw')

current_goal_label = tk.Label(frame_mid,text='Goal',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
current_goal_label.grid(row=1,column=0,sticky='nsw')

shift_goal_label = tk.Label(frame_mid,text='Shift Goal',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
shift_goal_label.grid(row=2,column=0,sticky='nsw')

efficiency_label = tk.Label(frame_mid,text='Efficiency',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
efficiency_label.grid(row=3,column=0,sticky='nsw')

bend_count = tk.Label(frame_mid,text='0',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
bend_count.grid(row=0,column=1,sticky='news')

current_goal= tk.Label(frame_mid,text='0',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
current_goal.grid(row=1,column=1,sticky='nwes')

shift_goal = tk.Label(frame_mid,text='0',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
shift_goal.grid(row=2,column=1,sticky='nwes')

efficiency = tk.Label(frame_mid,text='0%',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
efficiency.grid(row=3,column=1,sticky='nwes')

#define bottom frame widgets

input_goal_label = tk.Label(frame_btm,text='Input Goal',font=fonts[2],fg=font_color[0],bg=bgcolors[1],highlightbackground=bgcolors[1])
input_goal_label.grid(row=0,column=0,sticky='nwes')

input_goal_entry = tk.Entry(frame_btm,validate="key",font=fonts[2],fg=font_color[0],bg=bgcolors[3],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
input_goal_entry['validatecommand'] = (input_goal_entry.register(test_val),'%P','%d','%i')
input_goal_entry.grid(row=0,column=1,sticky='nwes')
input_goal_entry.focus_set()

resetbtn = tk.Button(frame_btm,text='Reset',font=fonts[2],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
resetbtn.grid(row=0,column=2,sticky='nwes')

undobtn = tk.Button(frame_btm,text='Undo',font=fonts[2],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
undobtn.grid(row=0,column=3,sticky='nwes')

# canvas = tk.Frame(width = win_width,height = win_height )
# canvas.place(height = win_height,width = win_width)

loop()
GPIO.add_event_detect(count_pin, GPIO.BOTH, callback=increase_count)
win.mainloop()
GPIO.cleanup()
