
import tkinter as tk
from PIL import ImageTk, Image
from time import strftime,sleep
from datetime import datetime,timedelta
import secrets
import re
import os
import RPi.GPIO as GPIO

bgcolors = ['#1a1a1a','#252526','#333333','#37373d'] # background colors
idcolors = ['red','yellow','green'] # identification colors that change based on the goal
font_color = ['#ffffff','black','#ff0000']
fonts = ['Helvetica 36 bold','Helvetica 92 bold','Helvetica 24','Helvetica 36','Helvetica 30 bold'] #top text , middle text, bottom text
loop_time = 20 #ms
blink_time = 500 #ms  must be a multipule of loop_time!
percent_colors = [75,90]
wait_time = .1 # seconds 
path = '/home/daikinfbn/Brake_Press_Counter4/'

def read_txt(lines):
    with open(path+'settings.txt','r') as variable_file:
        file_data = variable_file.readlines()
        data = []
        for line in lines:
                data.append(re.split(r'\s+',file_data[(line-1)])[1])
    return data

def write_txt(lines,strings):
    with open(path+'settings.txt','r') as variable_file:
        file_data = variable_file.readlines()
    for i,line in enumerate(lines):
        file_data[(line-1)] = re.split(r'\s+',file_data[(line-1)])[0] +' '+strings[i]+ '\n'
    with open(path+'settings.txt','w') as variable_file:
      variable_file.writelines(file_data)

def make_datetime_objects():
    global variables_data,count_pin,auto_reset_times,shift_times,break_times,epe_number
    epe_number  = read_txt([3])[0]
    variables_data = read_txt([(int(epe_number)+3),17,18,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,2])
    count_pin = int(variables_data[0])
    auto_reset_times = []
    shift_times = [[],[]]
    break_times = [[[],[],[]],[[],[],[]]]
    auto_reset_times.insert(0,datetime.now().replace(hour=int(variables_data[3].split(':')[0]),minute=int(variables_data[3].split(':')[1]))-timedelta(minutes=1))
    auto_reset_times.insert(1,datetime.now().replace(hour=int(variables_data[10].split(':')[0]),minute=int(variables_data[10].split(':')[1]))+timedelta(minutes=1))
    auto_reset_times.insert(2,datetime.now().replace(hour=int(variables_data[12].split(':')[0]),minute=int(variables_data[12].split(':')[1]))-timedelta(minutes=1))
    auto_reset_times.insert(3,datetime.now().replace(hour=int(variables_data[19].split(':')[0]),minute=int(variables_data[19].split(':')[1]))+timedelta(minutes=1))
    shift_times[0].append(datetime.now().replace(hour=int(variables_data[3].split(':')[0]),minute=int(variables_data[3].split(':')[1])))
    shift_times[0].append(datetime.now().replace(hour=int(variables_data[10].split(':')[0]),minute=int(variables_data[10].split(':')[1])))
    shift_times[1].append(datetime.now().replace(hour=int(variables_data[12].split(':')[0]),minute=int(variables_data[12].split(':')[1])))
    shift_times[1].append(datetime.now().replace(hour=int(variables_data[19].split(':')[0]),minute=int(variables_data[19].split(':')[1])))
    break_times[0][0].append(datetime.now().replace(hour=int(variables_data[4].split(':')[0]),minute=int(variables_data[4].split(':')[1])))
    break_times[0][0].append(datetime.now().replace(hour=int(variables_data[4].split(':')[0]),minute=int(variables_data[4].split(':')[1]))+timedelta(minutes=int(variables_data[5])))
    break_times[0][1].append(datetime.now().replace(hour=int(variables_data[6].split(':')[0]),minute=int(variables_data[6].split(':')[1])))
    break_times[0][1].append(datetime.now().replace(hour=int(variables_data[6].split(':')[0]),minute=int(variables_data[6].split(':')[1]))+timedelta(minutes=int(variables_data[7])))
    break_times[0][2].append(datetime.now().replace(hour=int(variables_data[8].split(':')[0]),minute=int(variables_data[8].split(':')[1])))
    break_times[0][2].append(datetime.now().replace(hour=int(variables_data[8].split(':')[0]),minute=int(variables_data[8].split(':')[1]))+timedelta(minutes=int(variables_data[9])))
    break_times[1][0].append(datetime.now().replace(hour=int(variables_data[13].split(':')[0]),minute=int(variables_data[13].split(':')[1])))
    break_times[1][0].append(datetime.now().replace(hour=int(variables_data[13].split(':')[0]),minute=int(variables_data[13].split(':')[1]))+timedelta(minutes=int(variables_data[14])))
    break_times[1][1].append(datetime.now().replace(hour=int(variables_data[15].split(':')[0]),minute=int(variables_data[15].split(':')[1])))
    break_times[1][1].append(datetime.now().replace(hour=int(variables_data[15].split(':')[0]),minute=int(variables_data[15].split(':')[1]))+timedelta(minutes=int(variables_data[16])))
    break_times[1][2].append(datetime.now().replace(hour=int(variables_data[17].split(':')[0]),minute=int(variables_data[17].split(':')[1])))
    break_times[1][2].append(datetime.now().replace(hour=int(variables_data[17].split(':')[0]),minute=int(variables_data[17].split(':')[1]))+timedelta(minutes=int(variables_data[18])))
    if shift_times[1][1].hour == 0:
        shift_times[1][1] += timedelta(days=1)

make_datetime_objects()

class CounterDisplay:
    global blink_time,loop_time,percent_colors,wait_time,path
    def __init__(self):
        self.already_reset = False
        self.past_index = 0
        self.prev_loop_time = 0
        self.past_values = [[0,0],[0,0],[0,0]] # [bendcount , shift goal]  store a few past values incase of accidental resets
        self.risen = True
        self.fallen = False
        self.can_count = True
        self.last_rise = datetime.now()
        self.last_fall = datetime.now()
        self.press_time = self.last_fall - self.last_rise
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(count_pin,GPIO.IN)
        GPIO.add_event_detect(count_pin, GPIO.BOTH, callback=self.increase_count)


        self.win = tk.Tk() 


        self.win.bind('<KP_Multiply>', self.change_focus_right)
        self.win.bind('<KP_Divide>', self.change_focus_left)
        self.win.bind('<KP_Subtract>',self.update_window)
        self.win.bind('<KP_Enter>',self.interact_widget)
        self.win.bind('<m>', self.change_focus_right)
        self.win.bind('<n>', self.change_focus_left)

#         self.win.bind('<*>', self.change_focus_right)
#         self.win.bind('</>', self.change_focus_left)
#         self.win.bind('<minus>', self.change_focus_left)


        self.win.bind('<Control-w>',self.close_window)
        self.win.bind('<Control-u>',self.update_window)
        self.win.bind('<Return>',self.interact_widget)
        self.win.bind('<b>',self.manual_bend_count)
        self.win.bind('<g>',self.manual_goal_count)
        self.win.bind('<o>',self.open_settings)

        self.win.geometry("1000x500")
        # self.win.attributes('-fullscreen',True)
        self.win.grid_columnconfigure(0,weight=1)
        self.win.grid_rowconfigure(0,weight=1)
        self.win.grid_rowconfigure(1,weight=10)
        self.win.grid_rowconfigure(2,weight=1)

        self.frame_top = tk.Frame(self.win,bg = bgcolors[1])
        self.frame_top.grid(row=0,column=0,sticky='nesw')
        self.frame_top.grid_columnconfigure(0,weight=1)
        self.frame_top.grid_columnconfigure(1,weight=2)
        self.frame_top.grid_columnconfigure(2,weight=1)
        self.frame_top.grid_rowconfigure(0,weight=1)

        self.frame_mid = tk.Frame(self.win,bg = bgcolors[0])
        self.frame_mid.grid(row=1,column=0,sticky='nesw')
        self.frame_mid.grid_rowconfigure(0,weight=1)
        self.frame_mid.grid_rowconfigure(1,weight=1)
        self.frame_mid.grid_rowconfigure(2,weight=1)
        self.frame_mid.grid_rowconfigure(3,weight=1)
        self.frame_mid.grid_columnconfigure(0,weight=1)
        self.frame_mid.grid_columnconfigure(1,weight=2)

        self.frame_btm = tk.Frame(self.win,bg = bgcolors[1])
        self.frame_btm.grid(row=2,column=0,sticky='nesw')
        self.frame_btm.grid_rowconfigure(0,weight=1)
        self.frame_btm.grid_columnconfigure(0,weight=1)
        self.frame_btm.grid_columnconfigure(1,weight=1)
        self.frame_btm.grid_columnconfigure(2,weight=1)
        self.frame_btm.grid_columnconfigure(3,weight=1)
        self.frame_btm.grid_columnconfigure(4,weight=1)

        #Defineing top frame widgets
        img = Image.open(path +"daikin_logo2.PNG")
        resized_image= img.resize((306,66), Image.ANTIALIAS)
        new_image= ImageTk.PhotoImage(resized_image)
        daikin_label = tk.Canvas(self.frame_top,height=70,width=240,bg=bgcolors[1],highlightbackground=bgcolors[1])
        daikin_label.grid(row=0,column=0,sticky='nswe')
        daikin_label.create_image(10,30,anchor=tk.W,image=new_image)
        machine = tk.Label(self.frame_top,text='EPE '+ epe_number,font=fonts[0],fg=font_color[0],bg=bgcolors[1])
        machine.grid(row=0,column=1,sticky='news')
        self.time = tk.Label(self.frame_top,text='',font=fonts[0],fg=font_color[0],bg=bgcolors[1])
        self.time.grid(row=0,column=2,sticky='nes')

        #defining middle frame widgets
        bend_count_label = tk.Label(self.frame_mid,text='Bend Count',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
        bend_count_label.grid(row=0,column=0,sticky='nsw')
        current_goal_label = tk.Label(self.frame_mid,text='Goal',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
        current_goal_label.grid(row=1,column=0,sticky='nsw')
        shift_goal_label = tk.Label(self.frame_mid,text='Shift Goal',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
        shift_goal_label.grid(row=2,column=0,sticky='nsw')
        efficiency_label = tk.Label(self.frame_mid,text='Efficiency',font=fonts[1],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
        efficiency_label.grid(row=3,column=0,sticky='nsw')
        self.bend_count = tk.Label(self.frame_mid,text='0',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
        self.bend_count.grid(row=0,column=1,sticky='news')
        self.current_goal= tk.Label(self.frame_mid,text='0',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
        self.current_goal.grid(row=1,column=1,sticky='nwes')
        self.shift_goal = tk.Label(self.frame_mid,text='0',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
        self.shift_goal.grid(row=2,column=1,sticky='nwes')
        self.efficiency = tk.Label(self.frame_mid,text='0%',font=fonts[1],fg=font_color[0],bg=bgcolors[0],highlightthickness=5 ,highlightbackground=bgcolors[0])
        self.efficiency.grid(row=3,column=1,sticky='nwes')

        #define bottom frame widgets
        input_goal_label = tk.Label(self.frame_btm,text='Input Goal',font=fonts[2],fg=font_color[0],bg=bgcolors[1],highlightbackground=bgcolors[1])
        input_goal_label.grid(row=0,column=0,sticky='nwes')
        self.input_goal_entry = tk.Entry(self.frame_btm,validate="key",font=fonts[2],fg=font_color[0],bg=bgcolors[3],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.input_goal_entry['validatecommand'] = (self.input_goal_entry.register(self.test_val),'%P','%d','%i')
        self.input_goal_entry.grid(row=0,column=1,sticky='nwes')
        self.input_goal_entry.focus_set()
        self.resetbtn = tk.Button(self.frame_btm,text='Reset',font=fonts[2],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.resetbtn.grid(row=0,column=2,sticky='nwes')
        self.undobtn = tk.Button(self.frame_btm,text='Undo',font=fonts[2],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.undobtn.grid(row=0,column=3,sticky='nwes')
        self.settingsbtn = tk.Button(self.frame_btm,text='Settings',font=fonts[2],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.settingsbtn.grid(row=0,column=4,sticky='nwes')

        if read_txt([2]) == 'True': # if the counter is update manually during a shift set the previous bend and shift count to the cached values
            self.bend_count['text'] = variables_data[1]
            self.shift_goal['text'] = variables_data[2]
            write_txt([2,17,18],['False','0','0'])
            variables_data[20] ='False'

        self.mainloop()
        self.win.mainloop()

    def test_val(self,inStr,acttyp,index): #Restricts the entry box to numbers and 4 charactures max
        if acttyp == '1': #insert
            if not inStr.isdigit() or int(index) >3 or inStr == '0'or len(inStr) > 4:
                return False
        return True

    def change_focus_right(self,event):
        event.widget.tk_focusNext().focus()

        if self.frame_btm.focus_get() == self.input_goal_entry:
            self.input_goal_entry['bg'] = bgcolors[3]
            self.settingsbtn['bg'] = bgcolors[1]

        if self.frame_btm.focus_get() == self.resetbtn:
            self.resetbtn['bg'] = bgcolors[3]
            self.input_goal_entry['bg'] = bgcolors[1]

        if self.frame_btm.focus_get() == self.undobtn:
            self.undobtn['bg'] = bgcolors[3]
            self.resetbtn['bg'] = bgcolors[1]

        if self.frame_btm.focus_get() == self.settingsbtn:
            self.settingsbtn['bg'] = bgcolors[3]
            self.undobtn['bg'] = bgcolors[1]

        return("break")

    def change_focus_left(self,event):
        event.widget.tk_focusPrev().focus()

        if self.frame_btm.focus_get() == self.input_goal_entry:
            self.input_goal_entry['bg'] = bgcolors[3]
            self.resetbtn['bg'] = bgcolors[1]

        if self.frame_btm.focus_get() == self.resetbtn:
            self.resetbtn['bg'] = bgcolors[3]
            self.undobtn['bg'] = bgcolors[1]

        if self.frame_btm.focus_get() == self.undobtn:
            self.undobtn['bg'] = bgcolors[3]
            self.settingsbtn['bg'] = bgcolors[1]

        if self.frame_btm.focus_get() == self.settingsbtn:
            self.settingsbtn['bg'] = bgcolors[3]
            self.input_goal_entry['bg'] = bgcolors[1]

        return("break")
    
    def close_window(self,event): # close the window
        write_txt([1],['True'])
        self.win.destroy()

    def interact_widget(self,event):
        if self.frame_btm.focus_get() == self.input_goal_entry and not self.input_goal_entry.get() == "":
            self.shift_goal['text'] = self.input_goal_entry.get()
            self.input_goal_entry.delete(0, tk.END)

        if self.frame_btm.focus_get() == self.resetbtn and not self.shift_goal.cget("text") == "0":
            self.past_values.append([int(self.bend_count.cget("text")),int(self.shift_goal.cget("text"))])
            self.past_values.pop(0)
            self.shift_goal['text'] = "0"
            self.current_goal['text'] = "0"
            self.bend_count['text'] = "0"
            self.efficiency['text'] = '0%'
            self.input_goal_entry.focus_set()
            self.input_goal_entry['bg'] = bgcolors[3]
            self.resetbtn['bg'] = bgcolors[1]

        if self.frame_btm.focus_get() == self.undobtn:
            if self.past_index  == 0:
                self.past_index = 2
            else:
                self.past_index -= 1
            self.shift_goal['text'] = str(self.past_values[self.past_index][1])
            self.bend_count['text'] = str(self.past_values[self.past_index][0])

        if self.frame_btm.focus_get() == self.settingsbtn:
            self.open_settings(event)
                
    def change_color(self,fg,bg):
        if self.bend_count['bg'] == bg:
            pass
        else:
            self.bend_count['bg'] = bg
            self.bend_count['fg'] = fg
            self.current_goal['bg'] = bg
            self.current_goal['fg'] = fg
            self.shift_goal['bg'] = bg
            self.shift_goal['fg'] = fg
            self.efficiency['bg'] = bg
            self.efficiency['fg'] = fg

    def update_color(self):
        if self.shift_goal.cget("text") == "0" and self.prev_loop_time == blink_time: # blink red
            self.change_color(font_color[1],idcolors[0])

        elif self.shift_goal.cget("text") == "0" and self.prev_loop_time == (blink_time*2): # blink to background color
            self.change_color(font_color[0],bgcolors[0])

        elif int(self.bend_count.cget("text")) < ((percent_colors[0]/100)*int(self.current_goal.cget('text'))) and not self.shift_goal.cget("text") == "0": # change to red when bend count is less than 75%
            self.change_color(font_color[1],idcolors[0])

        elif int(self.bend_count.cget("text")) >= ((percent_colors[0]/100)*int(self.current_goal.cget('text'))) and int(self.bend_count.cget("text")) < ((percent_colors[1]/100)*int(self.current_goal.cget('text'))) and not self.shift_goal.cget("text") == "0":
            self.change_color(font_color[1],idcolors[1])

        elif int(self.bend_count.cget("text")) >= ((percent_colors[1]/100)*int(self.current_goal.cget('text'))) and not self.shift_goal.cget("text") == "0": # change to green when bend count is greater than 90%
            self.change_color(font_color[1],idcolors[2])
         

        if self.prev_loop_time == 1000: # for the blinking red
            self.prev_loop_time = 0
        else:
            self.prev_loop_time += loop_time
        
    def mainloop(self):  # main loop loop
        self.time.config(text=strftime('%H:%M:%S'))  #loop clock text
        self.reset_update_counter()

        if self.current_goal.cget("text") != "0": # loop self.efficiency
            self.efficiency['text'] = str(round(int(self.bend_count.cget("text")) * 100 / int(self.current_goal.cget('text')))) + '%'

        if datetime.now() > shift_times[0][0] and datetime.now() <= shift_times[0][1]:
            shift_length = ((break_times[0][0][0] - shift_times[0][0]) + 
                            (break_times[0][1][0]-break_times[0][0][1]) + 
                            (break_times[0][2][0]-break_times[0][1][1]) + 
                            (shift_times[0][1] - break_times[0][2][1]))
            if datetime.now() < break_times[0][0][0] and datetime.now() > shift_times[0][0]:
                shift_percent = (datetime.now() - shift_times[0][0]) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()
            elif datetime.now() < break_times[0][1][0] and datetime.now() > break_times[0][0][1]:
                shift_percent = (datetime.now() - break_times[0][0][1] + (break_times[0][0][0] - shift_times[0][0])) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()
            elif datetime.now() < break_times[0][2][0] and datetime.now() > break_times[0][1][1]:
                shift_percent = (datetime.now() - break_times[0][1][1] + (break_times[0][0][0] - shift_times[0][0]) + (break_times[0][1][0]-break_times[0][0][1])) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()
            elif datetime.now() < shift_times[0][1] and datetime.now() >  break_times[0][2][1]:
                shift_percent = (datetime.now() - break_times[0][2][1] + (break_times[0][0][0] - shift_times[0][0]) + (break_times[0][1][0]-break_times[0][0][1]) + (break_times[0][2][0]-break_times[0][1][1])) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()

        elif datetime.now() > shift_times[1][0] and datetime.now() <= shift_times[1][1] and variables_data[11] == 'True' :
            shift_length = ((break_times[1][0][0] - shift_times[1][0]) + 
                            (break_times[1][1][0]-break_times[1][0][1]) + 
                            (break_times[1][2][0]-break_times[1][1][1]) + 
                            (shift_times[1][1] - break_times[1][2][1]))
            if int(shift_length.days) == -1:
                shift_length + timedelta(days=1)
            if datetime.now() < break_times[1][0][0] and datetime.now() > shift_times[1][0]:
                shift_percent = (datetime.now() - shift_times[1][0]) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()
            elif datetime.now() < break_times[1][1][0] and datetime.now() > break_times[1][0][1]:
                shift_percent = (datetime.now() - break_times[1][0][1] + (break_times[1][0][0] - shift_times[1][0])) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()
            elif datetime.now() < break_times[1][2][0] and datetime.now() > break_times[1][1][1]:
                shift_percent = (datetime.now() - break_times[1][1][1] + (break_times[1][0][0] - shift_times[1][0]) + (break_times[1][1][0]-break_times[1][0][1])) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()
            elif datetime.now() < shift_times[1][1] and datetime.now() >  break_times[1][2][1]:
                shift_percent = (datetime.now() - break_times[1][2][1] + (break_times[1][0][0] - shift_times[1][0]) + (break_times[1][1][0]-break_times[1][0][1]) + (break_times[1][2][0]-break_times[1][1][1])) / shift_length
                self.current_goal['text'] = str(round(shift_percent*int(self.shift_goal.cget('text'))))
                self.update_color()
        
        else:
            self.change_color(font_color[0],bgcolors[0])

        self.win.after(loop_time,self.loop)

    # TODO uncomment

    def increase_count(self,event):

        if GPIO.input(count_pin) == 0 and self.fallen == False:
            self.fallen = True
            self.risen = False
            self.can_count = True
            self.last_fall = datetime.now()
            
        if  GPIO.input(count_pin) == 1 and self.risen == False:
            self.risen = True
            self.fallen = False
            self.last_rise = datetime.now()
            self.press_time =  (self.last_fall - self.last_rise) * -1
        
        if self.press_time.total_seconds() > wait_time and self.fallen == False and self.can_count == True:
            self.can_count = False
            count = int(self.bend_count.cget('text'))
            count += 1
            self.bend_count['text'] = str(count)

    def reset_update_counter(self):
        #TODO double check auto reset times

        for t in auto_reset_times: #  times when the bend count and shift goal reset to zero
            if t.hour == datetime.now().hour and t.minute == datetime.now().minute and self.already_reset == False:
                self.past_values = [[0,0],[0,0],[0,0]]
                self.already_reset = True
                self.shift_goal['text'] = "0"
                self.current_goal['text'] = "0"
                self.bend_count['text'] = "0"
                self.efficiency['text'] = '0%'
                self.update_window(None)
                self.win.after(61000,self.can_reset)

    def can_reset(self):
        self.already_reset = False

    def manual_bend_count(self,event):  #manually increase to bend count by one used for testing
        count = int(self.bend_count.cget('text'))
        count += 1
        self.bend_count['text'] = str(count)

    def manual_goal_count(self,event):  #manually increase to goal count by one used for testing
        count = int(self.current_goal.cget('text'))
        count += 1
        self.current_goal['text'] = str(count)

    # TODO change to rpi update and add the etra ahead commit thing and the update cache
    def update_window(self,event):
            
        os.popen('sudo git -C ' + path + ' fetch https://DaikinFBN:' + secrets.secrets.get('GIT_TOKEN') + '@github.com/DaikinFBN/Brake_Press_Counter4.git')
        sleep(.1)
        update_status = os.popen('sudo git -C ' + path + ' status').read()
        if re.split(r'\s+',update_status)[6] == 'up':
            print('no update')
            pass
        # elif re.split(r'\s+',update_status)[6] == 'ahead':
           # print('no update')
           # pass
        else:
            print('update')
            write_txt([2,17,18],['True',str(self.bend_count.cget('text')),str(self.shift_goal.cget('text'))])
            self.win.destroy()

    def open_settings(self,event):
        Settings()

class Settings:
    def __init__(self):
        self.win = tk.Toplevel(bg = bgcolors[0])
        # self.win.geometry("1000x500")
        self.win.attributes('-fullscreen',True)
        
        # TODO uncomment

        self.win.bind('<KP_Multiply>', self.change_focus_right)
        self.win.bind('<KP_Divide>', self.change_focus_left)
        self.win.bind('<KP_Enter>',self.interact_widget)
        self.win.bind('<m>', self.change_focus_right)
        self.win.bind('<n>', self.change_focus_left)

#         self.win.bind('<*>', self.change_focus_right)
#         self.win.bind('</>', self.change_focus_left)


        self.win.bind('<Control-w>',self.close_window)
        self.win.bind('<Control-s>',self.save_values)
        self.win.bind('<Return>',self.interact_widget)

        #region Define settings frames
        self.win.grid_columnconfigure(0,weight=1)
        self.win.grid_rowconfigure(0,weight=1)
        self.win.grid_rowconfigure(1,weight=120)
        self.win.grid_rowconfigure(2,weight=1)

        self.frame_top = tk.Frame(self.win,bg = bgcolors[1])
        self.frame_top.grid(row=0,column=0,sticky='nesw')
        self.frame_top.grid_columnconfigure(0,weight=1)
        self.frame_top.grid_columnconfigure(1,weight=2)
        self.frame_top.grid_columnconfigure(2,weight=1)
        self.frame_top.grid_rowconfigure(0,weight=1)

        #region edit shift frames
        self.shift_frame = tk.Frame(self.win,bg = bgcolors[0],highlightbackground=bgcolors[0],highlightthickness=10,highlightcolor=bgcolors[0])
        self.shift_frame.grid(row=1,column=0,sticky='nesw')
        self.shift_frame.grid_rowconfigure(0,weight=6)
        self.shift_frame.grid_rowconfigure(1,weight=1)
        self.shift_frame.grid_rowconfigure(2,weight=4)
        self.shift_frame.grid_rowconfigure(3,weight=3)
        self.shift_frame.grid_columnconfigure(0,weight=1)
        self.shift_frame_top = tk.Frame(self.shift_frame,bg = bgcolors[0],highlightbackground=bgcolors[0],highlightthickness=5,highlightcolor=bgcolors[0])
        self.shift_frame_top.grid(row=0,column=0, sticky='nswe')
        self.shift_frame_top.grid_rowconfigure(0,weight=1)
        self.shift_frame_top.grid_rowconfigure(1,weight=1)
        self.shift_frame_top.grid_rowconfigure(2,weight=1)
        self.shift_frame_top.grid_columnconfigure(0,weight=1)
        self.shift_frame_top.grid_columnconfigure(1,weight=1)
        self.shift_frame_mid = tk.Frame(self.shift_frame,bg = bgcolors[0],highlightbackground=bgcolors[0],highlightthickness=5,highlightcolor=bgcolors[0])
        self.shift_frame_mid.grid(row=1,column=0, sticky='nswe')
        self.shift_frame_mid.grid_rowconfigure(0,weight=1)
        self.shift_frame_mid.grid_columnconfigure(0,weight=1)
        self.shift_frame_mid.grid_columnconfigure(1,weight=1)
        self.shift_frame_mid.grid_columnconfigure(2,weight=1)
        self.shift_frame_btm = tk.Frame(self.shift_frame,bg = bgcolors[0],highlightbackground=bgcolors[0],highlightthickness=5,highlightcolor=bgcolors[0])
        self.shift_frame_btm.grid(row=2,column=0, sticky='nswe')
        self.shift_frame_btm.grid_rowconfigure(0,weight=1)
        self.shift_frame_btm.grid_rowconfigure(1,weight=1)
        self.shift_frame_btm.grid_columnconfigure(0,weight=1)
        self.shift_frame_btm.grid_columnconfigure(1,weight=1)
        #endregion

        #region edit break frames
        self.break_frame = tk.Frame(self.win,bg = bgcolors[0],highlightbackground=bgcolors[0],highlightthickness=10,highlightcolor=bgcolors[0])
        self.break_frame.grid_rowconfigure(0,weight=3)
        self.break_frame.grid_rowconfigure(1,weight=3)
        self.break_frame.grid_rowconfigure(2,weight=1)
        self.break_frame.grid_columnconfigure(0,weight=1)
        self.break_frame_top = tk.Frame(self.break_frame,bg = bgcolors[0],highlightbackground=bgcolors[0],highlightthickness=5,highlightcolor=bgcolors[0])
        self.break_frame_top.grid(row=0,column=0 ,sticky='nswe')
        self.break_frame_top.grid_rowconfigure(0,weight=1)
        self.break_frame_top.grid_rowconfigure(1,weight=1)
        self.break_frame_top.grid_rowconfigure(2,weight=1)
        self.break_frame_top.grid_rowconfigure(3,weight=1)
        self.break_frame_top.grid_columnconfigure(0,weight=2)
        self.break_frame_top.grid_columnconfigure(1,weight=1)
        self.break_frame_top.grid_columnconfigure(2,weight=2)
        self.break_frame_top.grid_columnconfigure(3,weight=1)
        self.break_frame_btm = tk.Frame(self.break_frame,bg = bgcolors[0],highlightbackground=bgcolors[0],highlightthickness=5,highlightcolor=bgcolors[0])
        self.break_frame_btm.grid(row=1,column=0, sticky='nswe')
        self.break_frame_btm.grid_rowconfigure(0,weight=1)
        self.break_frame_btm.grid_rowconfigure(1,weight=1)
        self.break_frame_btm.grid_rowconfigure(2,weight=1)
        self.break_frame_btm.grid_columnconfigure(0,weight=2)
        self.break_frame_btm.grid_columnconfigure(1,weight=1)
        self.break_frame_btm.grid_columnconfigure(2,weight=2)
        self.break_frame_btm.grid_columnconfigure(3,weight=1)
        #endregion

        self.frame_btm = tk.Frame(self.win,bg = bgcolors[1])
        self.frame_btm.grid(row=2,column=0,sticky='nesw')
        self.frame_btm.grid_rowconfigure(0,weight=1)
        self.frame_btm.grid_columnconfigure(0,weight=1)
        self.frame_btm.grid_columnconfigure(1,weight=1)
        self.frame_btm.grid_columnconfigure(2,weight=1)
        #endregion

        #region Defineing top frame widgets
        img = Image.open(path +"daikin_logo2.PNG")
        resized_image= img.resize((306,66), Image.ANTIALIAS)
        new_image= ImageTk.PhotoImage(resized_image)
        daikin_label = tk.Canvas(self.frame_top,height=20,width=240,bg=bgcolors[1],highlightbackground=bgcolors[1])
        daikin_label.grid(row=0,column=0,sticky='nswe')
        daikin_label.create_image(10,30,anchor=tk.W,image=new_image)
        machine = tk.Label(self.frame_top,text='EPE '+ epe_number,font=fonts[0],fg=font_color[0],bg=bgcolors[1])
        machine.grid(row=0,column=1,sticky='news')
        self.time = tk.Label(self.frame_top,text='',font=fonts[0],fg=font_color[0],bg=bgcolors[1])
        self.time.grid(row=0,column=2,sticky='nes')
        #endregion

        #region define edit shift widgets
        self.edit_shift = tk.Label(self.shift_frame_top,text='Edit Shift Times',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        self.edit_shift.grid(row=0,column=0, sticky='nswe')
        self.edit_break = tk.Label(self.shift_frame_top,text='Edit Break Times',font=fonts[3],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
        self.edit_break.grid(row=0,column=1, sticky='nswe')
        first_start = tk.Label(self.shift_frame_top,text='Shift Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        first_start.grid(row=1,column=0, sticky='nswe')
        first_end = tk.Label(self.shift_frame_top,text='Shift End',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        first_end.grid(row=2,column=0,sticky='nswe')
        self.first_start_entry = tk.Entry(self.shift_frame_top,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.first_start_entry['validatecommand'] = (self.first_start_entry.register(self.test_val4),'%P','%d','%i')
        self.first_start_entry.insert(0,variables_data[3].split(':')[0]+variables_data[3].split(':')[1])
        self.first_start_entry.grid(row=1,column=1,sticky='nwes')
        self.first_end_entry = tk.Entry(self.shift_frame_top,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.first_end_entry['validatecommand'] = (self.first_end_entry.register(self.test_val4),'%P','%d','%i')
        self.first_end_entry.insert(0,variables_data[10].split(':')[0]+variables_data[10].split(':')[1])
        self.first_end_entry.grid(row=2,column=1,sticky='nwes')
        add_second_shift = tk.Label(self.shift_frame_mid,text='Add Second Shift   ',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        add_second_shift.grid(row=0,column=0,sticky='nswe')
        self.yesbtn = tk.Button(self.shift_frame_mid,text='Yes',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.yesbtn.grid(row=0,column=1,sticky='nwes')
        self.nobtn = tk.Button(self.shift_frame_mid,text='No',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.nobtn.grid(row=0,column=2,sticky='nwes')
        if variables_data[11] == 'True':
            self.yesbtn['bg'] = bgcolors[3]
        else:    
            self.nobtn['bg'] = bgcolors[3]
            self.shift_frame_btm.grid_forget()
        second_start = tk.Label(self.shift_frame_btm,text='Shift Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        second_start.grid(row=0,column=0,sticky='nswe')
        second_end = tk.Label(self.shift_frame_btm,text='Shift End',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        second_end.grid(row=1,column=0,sticky='nswe')
        self.second_start_entry = tk.Entry(self.shift_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.second_start_entry['validatecommand'] = (self.second_start_entry.register(self.test_val4),'%P','%d','%i')
        self.second_start_entry.insert(0,variables_data[12].split(':')[0]+variables_data[12].split(':')[1])
        self.second_start_entry.grid(row=0,column=1,sticky='nwes')
        self.second_end_entry = tk.Entry(self.shift_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.second_end_entry['validatecommand'] = (self.second_end_entry.register(self.test_val40),'%P','%d','%i')
        self.second_end_entry.insert(0,variables_data[19].split(':')[0]+variables_data[19].split(':')[1])
        self.second_end_entry.grid(row=1,column=1,sticky='nwes')
        self.shift_warning_label = tk.Label(self.shift_frame,text=' ',font=fonts[4],fg=font_color[2],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[0],highlightthickness=5)
        self.shift_warning_label.grid(row=3,column=0, sticky='nswe')
        #endregion

        #region define edit break widgets
        self.edit_shift = tk.Label(self.break_frame_top,text='Edit Shift Times',font=fonts[3],fg=font_color[0],bg=bgcolors[0],borderwidth=0)
        self.edit_shift.grid(row=0,column=0,columnspan=2, sticky='nswe')
        self.edit_break = tk.Label(self.break_frame_top,text='Edit Break Times',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        self.edit_break.grid(row=0,column=2,columnspan=2, sticky='nswe')
        shift1break1 = tk.Label(self.break_frame_top,text='Break 1 Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift1break1.grid(row=1,column=0, sticky='nswe')
        shift1break1length = tk.Label(self.break_frame_top,text='Length',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift1break1length.grid(row=1,column=2, sticky='nswe')
        shift1_lunch = tk.Label(self.break_frame_top,text='Lunch Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift1_lunch.grid(row=2,column=0, sticky='nswe')
        shift1_lunch_length = tk.Label(self.break_frame_top,text='Length',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift1_lunch_length.grid(row=2,column=2, sticky='nswe')
        shift1break2 = tk.Label(self.break_frame_top,text='Break 2 Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift1break2.grid(row=3,column=0,sticky='nswe')
        shift1break2length = tk.Label(self.break_frame_top,text='Length',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift1break2length.grid(row=3,column=2,sticky='nswe')
        shift2break1 = tk.Label(self.break_frame_btm,text='Break 1 Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift2break1.grid(row=0,column=0, sticky='nswe')
        shift2break1length = tk.Label(self.break_frame_btm,text='Length',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift2break1length.grid(row=0,column=2, sticky='nswe')
        shift2_lunch = tk.Label(self.break_frame_btm,text='Lunch Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift2_lunch.grid(row=1,column=0, sticky='nswe')
        shift2_lunch_length = tk.Label(self.break_frame_btm,text='Length',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift2_lunch_length.grid(row=1,column=2, sticky='nswe')
        shift2break2 = tk.Label(self.break_frame_btm,text='Break 2 Start',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift2break2.grid(row=2,column=0,sticky='nswe')
        shift2break2length = tk.Label(self.break_frame_btm,text='Length',font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0)
        shift2break2length.grid(row=2,column=2,sticky='nswe')
        self.break_warning_label = tk.Label(self.break_frame,text=' ',font=fonts[4],fg=font_color[2],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[0],highlightthickness=5)
        self.break_warning_label.grid(row=2,column=0, sticky='nswe')
        self.shift1break1_entry = tk.Entry(self.break_frame_top,validate="key",justify=tk.CENTER,text='test', font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift1break1_entry['validatecommand'] = (self.shift1break1_entry.register(self.test_val4),'%P','%d','%i')
        self.shift1break1_entry.insert(0,variables_data[4].split(':')[0]+variables_data[4].split(':')[1])
        self.shift1break1_entry.grid(row=1,column=1,sticky='nwes')
        self.shift1break1length_entry = tk.Entry(self.break_frame_top,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift1break1length_entry['validatecommand'] = (self.shift1break1length_entry.register(self.test_val4),'%P','%d','%i')
        self.shift1break1length_entry.insert(0,variables_data[5])
        self.shift1break1length_entry.grid(row=1,column=3,sticky='nwes')
        self.shift1lunch_entry = tk.Entry(self.break_frame_top,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift1lunch_entry['validatecommand'] = (self.shift1lunch_entry.register(self.test_val4),'%P','%d','%i')
        self.shift1lunch_entry.insert(0,variables_data[6].split(':')[0]+variables_data[6].split(':')[1])
        self.shift1lunch_entry.grid(row=2,column=1,sticky='nwes')
        self.shift1lunchlength_entry = tk.Entry(self.break_frame_top,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift1lunchlength_entry['validatecommand'] = (self.shift1lunchlength_entry.register(self.test_val4),'%P','%d','%i')
        self.shift1lunchlength_entry.insert(0,variables_data[7])
        self.shift1lunchlength_entry.grid(row=2,column=3,sticky='nwes')
        self.shift1break2_entry = tk.Entry(self.break_frame_top,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift1break2_entry['validatecommand'] = (self.shift1break2_entry.register(self.test_val4),'%P','%d','%i')
        self.shift1break2_entry.insert(0,variables_data[8].split(':')[0]+variables_data[8].split(':')[1])
        self.shift1break2_entry.grid(row=3,column=1,sticky='nwes')
        self.shift1break2length_entry = tk.Entry(self.break_frame_top,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift1break2length_entry['validatecommand'] = (self.shift1break2length_entry.register(self.test_val4),'%P','%d','%i')
        self.shift1break2length_entry.insert(0,variables_data[9])
        self.shift1break2length_entry.grid(row=3,column=3,sticky='nwes')
        self.shift2break1_entry = tk.Entry(self.break_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift2break1_entry['validatecommand'] = (self.shift2break1_entry.register(self.test_val4),'%P','%d','%i')
        self.shift2break1_entry.insert(0,variables_data[13].split(':')[0]+variables_data[13].split(':')[1])
        self.shift2break1_entry.grid(row=0,column=1,sticky='nwes')
        self.shift2break1length_entry = tk.Entry(self.break_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift2break1length_entry['validatecommand'] = (self.shift2break1length_entry.register(self.test_val4),'%P','%d','%i')
        self.shift2break1length_entry.insert(0,variables_data[14])
        self.shift2break1length_entry.grid(row=0,column=3,sticky='nwes')
        self.shift2lunch_entry = tk.Entry(self.break_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift2lunch_entry['validatecommand'] = (self.shift2lunch_entry.register(self.test_val4),'%P','%d','%i')
        self.shift2lunch_entry.insert(0,variables_data[15].split(':')[0]+variables_data[15].split(':')[1])
        self.shift2lunch_entry.grid(row=1,column=1,sticky='nwes')
        self.shift2lunchlength_entry = tk.Entry(self.break_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift2lunchlength_entry['validatecommand'] = (self.shift2lunchlength_entry.register(self.test_val4),'%P','%d','%i')
        self.shift2lunchlength_entry.insert(0,variables_data[16])
        self.shift2lunchlength_entry.grid(row=1,column=3,sticky='nwes')
        self.shift2break2_entry = tk.Entry(self.break_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift2break2_entry['validatecommand'] = (self.shift2break2_entry.register(self.test_val4),'%P','%d','%i')
        self.shift2break2_entry.insert(0,variables_data[17].split(':')[0]+variables_data[17].split(':')[1])
        self.shift2break2_entry.grid(row=2,column=1,sticky='nwes')
        self.shift2break2length_entry = tk.Entry(self.break_frame_btm,validate="key",justify=tk.CENTER,font=fonts[3],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[2],insertbackground=font_color[0])
        self.shift2break2length_entry['validatecommand'] = (self.shift2break2length_entry.register(self.test_val4),'%P','%d','%i')
        self.shift2break2length_entry.insert(0,variables_data[18])
        self.shift2break2length_entry.grid(row=2,column=3,sticky='nwes')
        #endregion

        #region define bottom frame widgets
        self.change_tabbtn = tk.Button(self.frame_btm,text='Edit Break Times',font=fonts[2],fg=font_color[0],bg=bgcolors[3],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.change_tabbtn.grid(row=0,column=0,sticky='nwes')
        self.change_tabbtn.focus_set()
        self.savebtn = tk.Button(self.frame_btm,text='Save',font=fonts[2],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.savebtn.grid(row=0,column=1,sticky='nwes')
        self.closebtn = tk.Button(self.frame_btm,text='Close',font=fonts[2],fg=font_color[0],bg=bgcolors[1],borderwidth=0,highlightbackground=bgcolors[1],activebackground=bgcolors[2],activeforeground=font_color[0])
        self.closebtn.grid(row=0,column=2,sticky='nwes')
        #endregion

        self.loop()
        self.win.mainloop()

    def test_val40(self,inStr,acttyp,index): #Restricts the entry box to numbers and 4 charactures max
        if acttyp == '1': #insert
            if not inStr.isdigit() or int(index) >3 or len(inStr) > 4:
                return False
        return True

    def test_val4(self,inStr,acttyp,index): #Restricts the entry box to numbers and 4 charactures max and no zeros
        if acttyp == '1': #insert
            if not inStr.isdigit() or int(index) >3 or inStr == '0' or len(inStr) > 4:
                return False
        return True

    def test_val2(self,inStr,acttyp,index): #Restricts the entry box to numbers and 2 charactures max and no zeros
        if acttyp == '1': #insert
            if not inStr.isdigit() or int(index) >1 or len(inStr) > 2:
                return False
        return True

    def change_focus_right(self,event):
        last_focus = self.shift_frame.focus_get()
        event.widget.tk_focusNext().focus()
        current_focus = self.shift_frame.focus_get()
        current_focus['bg'] = bgcolors[3]
        if last_focus == self.yesbtn and variables_data[11] == 'True':
            last_focus['bg'] = bgcolors[3]
        elif last_focus == self.nobtn and variables_data[11] == 'False':
            last_focus['bg'] = bgcolors[3]
        else:    
            last_focus['bg'] = bgcolors[1]
        return("break")

    def change_focus_left(self,event):
        last_focus = self.shift_frame.focus_get()
        event.widget.tk_focusPrev().focus()
        current_focus = self.shift_frame.focus_get()
        current_focus['bg'] = bgcolors[3]
        if last_focus == self.yesbtn and variables_data[11] == 'True':
            last_focus['bg'] = bgcolors[3]
        elif last_focus == self.nobtn and variables_data[11] == 'False':
            last_focus['bg'] = bgcolors[3]
        else:    
            last_focus['bg'] = bgcolors[1]
        return("break")

    def interact_widget(self,event):
        
        if self.change_tabbtn['text'] == 'Edit Break Times' and self.frame_btm.focus_get() == self.change_tabbtn:
            self.change_tabbtn['text'] = 'Edit Shift Times'
            self.shift_frame.grid_forget()
            self.break_frame.grid(row=1,column=0,sticky='nesw')
            if variables_data[11] == 'False':
                self.break_frame_btm.grid_forget()
            return

        if self.change_tabbtn['text'] == 'Edit Shift Times'and self.frame_btm.focus_get() == self.change_tabbtn:
            self.change_tabbtn['text'] = 'Edit Break Times'
            self.break_frame.grid_forget()
            self.shift_frame.grid(row=1,column=0,sticky='nesw')
            if variables_data[11] == 'False':
                self.break_frame_btm.grid_forget()
            return

        if self.frame_btm.focus_get() == self.savebtn:
            self.save_values(event)

        if self.frame_btm.focus_get() == self.closebtn:
            self.close_window(event)

        if self.shift_frame_mid.focus_get() == self.yesbtn and variables_data[11] == 'False':
            self.shift_frame_btm.grid(row=2,column=0, sticky='nswe')
            self.break_frame_btm.grid(row=1,column=0, sticky='nswe')
            write_txt([28],['True'])
            variables_data[11] = 'True'
            self.yesbtn['bg'] = bgcolors[3]
            self.nobtn['bg'] = bgcolors[1]

        if self.shift_frame_mid.focus_get() == self.nobtn and variables_data[11] == 'True':
            self.shift_frame_btm.grid_forget()
            self.break_frame_btm.grid_forget()
            write_txt([28],['False'])
            variables_data[11] = 'False'
            self.yesbtn['bg'] = bgcolors[1]
            self.nobtn['bg'] = bgcolors[3]
            
    def loop(self):  # main loop loop
        self.time.config(text=strftime('%H:%M:%S'))  #loop clock text
        self.win.after(loop_time,self.loop)

    def save_values(self,event):\
        
        if variables_data[11] == 'True':
            entry_feilds = [ [self.first_start_entry,4]
                            ,[self.shift1break1_entry,4]
                            ,[self.shift1break1length_entry,2]
                            ,[self.shift1lunch_entry,4]
                            ,[self.shift1lunchlength_entry,2]
                            ,[self.shift1break2_entry,4]
                            ,[self.shift1break2length_entry,2]
                            ,[self.first_end_entry,4]
                            ,[self.second_start_entry,4]
                            ,[self.shift2break1_entry,4]
                            ,[self.shift2break1length_entry,2]
                            ,[self.shift2lunch_entry,4]
                            ,[self.shift2lunchlength_entry,2]
                            ,[self.shift2break2_entry,4]
                            ,[self.shift2break2length_entry,2]
                            ,[self.second_end_entry,4]]
        else:
            entry_feilds = [ [self.first_start_entry,4]
                            ,[self.shift1break1_entry,4]
                            ,[self.shift1break1length_entry,2]
                            ,[self.shift1lunch_entry,4]
                            ,[self.shift1lunchlength_entry,2]
                            ,[self.shift1break2_entry,4]
                            ,[self.shift1break2length_entry,2]
                            ,[self.first_end_entry,4]]           

        warning_msg = 'ERROR: '

        for i,entry in enumerate(entry_feilds):
            entry[0]['highlightthickness'] = 0
            if entry[1] == 2: # check two digit number entrys
                if not len(entry[0].get()) >= 1 or not int(entry[0].get()) <= 60:
                    warning_msg += 'You must input a break lengths and it must less than 60 minutes long\n'
                    entry[0]['highlightthickness'] = 5
                    entry[0]['highlightcolor']='red'
                    entry[0]['highlightbackground']='red'

                    entry[0].focus()
                    entry[0]['bg'] = bgcolors[3]
                    self.savebtn['bg'] = bgcolors[1]
                    break
            if entry[1] == 4: # check four digit number entrys
                if  not len(entry[0].get()) >= 3 or int(entry[0].get()) > 2359 or int(entry[0].get()[-2:]) > 59:
                    warning_msg += 'You must input a value in military time\nIt has to be at least 3 digits long\n'
                    entry[0]['highlightthickness'] = 5
                    entry[0]['highlightcolor']='red'
                    entry[0]['highlightbackground']='red'
                    
                    entry[0].focus()
                    entry[0]['bg'] = bgcolors[3]
                    self.savebtn['bg'] = bgcolors[1]
                    break

            # creat current and prevous enrty datetime objects
            if entry[1] == 2: 
                prev_entry = datetime.now().replace(hour=int(entry_feilds[i-1][0].get()[-4:-2]),minute=int(entry_feilds[i-1][0].get()[-2:]))
                this_entry = (prev_entry+timedelta(minutes=int(entry[0].get())))
            elif entry_feilds[i-1][1] == 2:
                this_entry = datetime.now().replace(hour=int(entry[0].get()[-4:-2]),minute=int(entry[0].get()[-2:]))
                prev_entry = (datetime.now().replace(hour=int(entry_feilds[i-2][0].get()[-4:-2]),minute=int(entry_feilds[i-2][0].get()[-2:]))+timedelta(minutes=int(entry_feilds[i-1][0].get())))
            else:
                prev_entry = datetime.now().replace(hour=int(entry_feilds[i-1][0].get()[-4:-2]),minute=int(entry_feilds[i-1][0].get()[-2:]))
                this_entry = datetime.now().replace(hour=int(entry[0].get()[-4:-2]),minute=int(entry[0].get()[-2:]))
            
            # check edge cases and change te datetime objects as nesessary
            if entry[0] == self.second_end_entry and this_entry < datetime.now().replace(hour=int(entry_feilds[0][0].get()[-4:-2]),minute=int(entry_feilds[0][0].get()[-2:])):
                this_entry += timedelta(days=1)
            elif entry[0] == self.first_start_entry and prev_entry > this_entry:
                this_entry += timedelta(days=1)
            elif variables_data[11] == 'False' and entry[0] == self.first_start_entry:
                    temp = prev_entry
                    prev_entry = this_entry
                    this_entry = temp

            # compare the prevous entry with the current entry to find collisions
            if not this_entry > prev_entry:
                entry[0]['highlightthickness'] = 5
                entry[0]['highlightcolor']='red'
                entry[0]['highlightbackground']='red'
                entry_feilds[i-1][0]['highlightthickness'] = 5
                entry_feilds[i-1][0]['highlightcolor']='red'
                entry_feilds[i-1][0]['highlightbackground']='red'
                entry[0].focus()
                entry[0]['bg'] = bgcolors[3]
                self.savebtn['bg'] = bgcolors[1]
                warning_msg += 'Break times must happen within the shift window\nBreak times must not overlap with eachother\nShift times must not overlap'
                break

        # change shift times if all conditions are correct
        if warning_msg == 'ERROR: ':
            warning_msg = 'New Shift and Breaks times saved!'
            self.shift_warning_label['text'] = warning_msg
            self.shift_warning_label['fg'] = font_color[0]
            self.break_warning_label['text'] = warning_msg
            self.break_warning_label['fg'] = font_color[0]
            self.new_times = []
            
            # write all shift times if both are active
            if variables_data[11] == 'True':
                for entry in entry_feilds:
                    if len(entry[0].get()) <= 2:
                        self.new_times.append(entry[0].get())
                    else:
                        self.new_times.append(entry[0].get()[-4:-2]+':'+entry[0].get()[-2:])
                write_txt([20,21,22,23,24,25,26,27,29,30,31,32,33,34,35,36],self.new_times)
            
            # write only first shifts times when second shift is off
            else:
                for entry in entry_feilds:
                    if len(entry[0].get()) <= 2:
                        self.new_times.append(entry[0].get())
                    else:
                        self.new_times.append(entry[0].get()[-4:-2]+':'+entry[0].get()[-2:])
                write_txt([20,21,22,23,24,25,26,27],self.new_times)
                
            # remake datetime objects for counter
            make_datetime_objects()
        
        # show the error and the two time boxes that caused it
        else:
            self.shift_warning_label['text'] = warning_msg
            self.shift_warning_label['fg'] = font_color[2]
            self.break_warning_label['text'] = warning_msg
            self.break_warning_label['fg'] = font_color[2]

    def close_window(self,event): # close the window
        self.win.destroy()
