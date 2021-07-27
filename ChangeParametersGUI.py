# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 22:01:23 2020

@author: Lenovo
"""

import tkinter as tk
from tkinter import messagebox
from tkinter import *

"""
    GUI
"""
fields = 'Message 1','Message 2', 'Message 3', 'Video Duration', 'Detection Distance', 'Humidity', 'Message Interval'

def fetch(root,entries):
    global message1
    global message2
    global message3  
    global videoDuration
    global detectDistance
    global userHumidity
    global userInterval   

    print(entries[0][1].get())
    print(entries[1][1].get())
    print(entries[2][1].get())
    
    if entries[3][1].get().isdigit==False or (entries[4][1].get()).isdigit()==False or (entries[3][1].get()).isdigit()==False or (entries[3][1].get()).isdigit()==False:
        messagebox.showinfo("-- ERROR --", "Enter numbers only for last 4 entries", icon="warning")        
    else:
        message1  = entries[0][1].get()
        message2 = entries[1][1].get()
        message3 = entries[2][1].get()
        videoDuration = entries[3][1].get()
        detectDistance = entries[4][1].get()
        userHumidity = entries[5][1].get()
        userInterval = entries[6][1].get()
    
        messagebox.showinfo("-- COMPLETE --", "Changes Saved.", icon="info")
            
        
def makeform(root, fields):
    entries = []
    i=0
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=30, text=field, anchor='w')
        ent = tk.Entry(row)
        ent.config(show='')
        if i==0:
            ent.insert(0,message1)
        elif i==1:
            ent.insert(0,message2)            
        elif i==2:
            ent.insert(0,message3)  
        elif i==3:
            ent.insert(0,videoDuration)  
        elif i==4:
            ent.insert(0,detectDistance)  
        elif i==5:
            ent.insert(0,userHumidity) 
        elif i==6:
            ent.insert(0,userInterval)
            
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))
        i+=1
    return entries


#User Defined Video Duration 
global videoDuration
videoDuration = 60
#User Defined Detection Distance
global detectDistance
detectDistance = 10
#User Defined Humidity 
global userHumidity
userHumidity = 1000
#User Defined Alert Interval (IN SECONDS)
global userInterval
userInterval = 5
#User Defined Alert for Humidity and Object Detected
global message1
message1="Person Outside and It is Raining"
#User Defined Alert for Humidity and No Object Detected
global message2
message2="Keep the Laundry"
#User Defined Alert for Object Detected
global message3
message3="Person Outside"

"""
Main Running Code
"""

def main():
    
    """main Tk()"""
    root = tk.Tk()
    root.title("Log In Mr Potato")
    MainFrame = tk.Frame(root, width=500, height=100)
    MainFrame.pack(fill=None,expand=False)

    """keybind"""
    ents = makeform(root, fields)
    root.bind('<Return>', (lambda event, e=ents: fetch(root,e)))   

    """buttons"""
    b1 = tk.Button(root, text='Save',
                command=(lambda e=ents: fetch(root,e)))
    b2 = tk.Button(root, text='Exit', command=root.destroy)
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2.pack(side=tk.RIGHT, padx=5, pady=5)
    
    root.mainloop()
