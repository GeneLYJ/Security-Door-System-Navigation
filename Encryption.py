# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 22:01:23 2020

@author: Lenovo
"""
import numpy as np
import random
import tkinter as tk
from tkinter import messagebox


number = ['0','1','2','3','4','5','6','7','8','9']
symbol = ['!',"@","#","$",'%','^','&','*',')','/','(','+','=','-',';',':','<','>'\
    ,',','.','~',']','[','?']
uppercase = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'\
    , 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
lowercase = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o'\
    , 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

"""
	Your ID and PW @ line 191 and 193
"""

"""
ENCRYPTION AND DECRYTION SECTION
"""
def randNums(n,a,b,s,key):
    #finds n random ints in [a,b] with sum of s
    hit = False
    random.seed(key)
    while not hit:
        total, count = 0,0
        nums = []
        while total < s and count < n:
            r = random.randint(a,b)
            total += r
            count += 1
            nums.append(r)
        if total == s and count == n: hit = True
    return nums

def findKey(userName):
    index = 0
    for letter in userName:
        if letter in uppercase:
            index += uppercase.index(letter)
        elif letter in lowercase:
            index += lowercase.index(letter)
        elif letter in symbol:
            index += symbol.index(letter)
        elif letter in number:
            index += number.index(letter)
    return index**2


def encrypt(realText, key):
 	outText = ""
 	cryptText = []
 	cryptText1 = []
 	cryptText2 = []
 	cryptText3 = []
 	
 	#print(len(hashSalt))
 	#UC - d2@
 	#lc - 3@V
 	#sym - Dv2
 	#No - #Cd
 	
 	for letter in realText:
		
		 if letter in uppercase:
 			index = uppercase.index(letter)
 			selection = 1								
 			
		 elif letter in lowercase:
 			index = lowercase.index(letter)
 			selection = 2
 			
		 elif letter in symbol:
 			index = symbol.index(letter)
 			selection = 3
 			
		 elif letter in number:
 			index = number.index(letter)
 			selection = 4
		
		 if index == 0:
 			array = [0,0,0]
		 else:
 			array = randNums(3,0,9,index,key)
		
		 if selection == 1:
 			cryptText1.extend(lowercase[10 + array[0]])
 			cryptText2.extend(number[array[1]])
 			cryptText3.extend(symbol[array[2]])
 			
		 elif selection == 2:

 			cryptText1.extend(number[array[0]])
 			cryptText2.extend(symbol[23-array[1]])
 			cryptText3.extend(uppercase[array[2]])
 							
		 elif selection == 3:

 			cryptText1.extend(uppercase[array[0]])
 			cryptText2.extend(lowercase[20 - array[1]])
 			cryptText3.extend(number[array[2]])
 			
		 elif selection == 4:

 			cryptText1.extend(symbol[array[0]])
 			cryptText2.extend(uppercase[25-array[1]])
 			cryptText3.extend(lowercase[array[2]])
		
 	cryptText = np.concatenate((cryptText1,cryptText2,cryptText3))
 	for x in cryptText:
		 outText += x
		
 	return outText


"""
	GUI
"""
fields = 'username','password'
y = 0
def fetch(root,entries):
	
	# extract ID and PW
	text  = entries[0][1].get()
	text2 = entries[1][1].get()
	state = 3
	
	#encrypt both ID and PW and send to server
	if text == "" or text2 == "":
		messagebox.showinfo("-- ERROR --", "Do Not Leave It Blank!", icon="warning")
	else:
		key = findKey(text)
		cipherPW = encrypt(text2, key)
		print("Key and PW are:")
		print("Key:",key)
		print("PW",cipherPW)
		
		print("\nsending to local server....\n")
		# send cipherText to server
		send2Server = Server(text,cipherPW)
		# server check if it matches any of the ID and PW in server
		state = send2Server.Affirmation()
	
	# Server send the status back to user
	if state == 0:
		messagebox.showinfo("-- ERROR --", "Wrong User ID or Wrong Password!", icon="warning")
	elif state == -1:
		messagebox.showinfo("-- ERROR --", "Wrong User ID or Wrong Password!", icon="warning")
	elif state == 1:
		messagebox.showinfo("-- COMPLETE --", "You Have Now Logged In.", icon="info")
		global y
		y = 1
		root.destroy()

				
		
def makeform(root, fields):
    entries = []
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=30, text=field, anchor='w')
        ent = tk.Entry(row)
        ent.config(show='')
        ent.after(1,lambda: ent.config(show='*'))
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field, ent))
    return entries

def stop():
	global y
	return y

"""
	Server 
""" 
class Server:
	def __init__(self,ID,cipherPW):
		self._ID = ID
		self._cipherPW = cipherPW
		
	def PersonalStorage(self,index=None):
		ID = ["Eugene","Wong","Darryl","Joseph"]
        # original password 
        # PW = ["1sMyPwStr0ng?","1sMyPwStr0ng!","1sMyPwStr0ng.","1sMyPwStr0ng/"]
		PW = ["!8l9m6s76!33JZ:8;4<8,]Z~?obC$G/J#HJaHD8","!3k8s8n83!50AZ:8:5;8~>Z>~ubH%I#F*IIaCD0","!7n9o8r57!25FZ;7<9:9>[Z]?obC#I#G#IJaJB8","!7m6q8r88!40AZ~7;6<3;,Z[[mbI$J$H)CEaIF1"]
		if index is None:
			return len(ID)
		else:
			return ID[index],PW[index],len(ID)
		
	def Affirmation(self):
		length = self.PersonalStorage()
		for x in range(length):
			user_ID = self.PersonalStorage(x)
			if self._ID==user_ID[0]:
				if self._cipherPW==user_ID[1]:
					return 1
					break
				else:
					return -1
					break
		return 0
				

"""
Main Function
"""
def main():
	
	"""main Tk()"""
	root = tk.Tk()
	root.title("Log In Mr Potato")
	MainFrame = tk.Frame(root, width=100, height=100)
	MainFrame.pack(fill=None,expand=False)

	"""keybind"""
	ents = makeform(root, fields)
	root.bind('<Return>', (lambda event, e=ents: fetch(root,e)))   

	"""buttons"""
	b1 = tk.Button(root, text='Login',
				command=(lambda e=ents: fetch(root,e)))
	b2 = tk.Button(root, text='Quit', command=root.destroy)
	b1.pack(side=tk.LEFT, padx=5, pady=5)
	b2.pack(side=tk.RIGHT, padx=5, pady=5)
	root.mainloop()
	#v = stop()
	#print(v)
	print("good, it loads")