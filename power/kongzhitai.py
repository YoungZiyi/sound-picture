# -*- coding: utf-8 -*-
#!/usr/bin/env python

import Tkinter
from BxtLogger import *
import Device
import time
from Tkconstants import *
import Device

top = Tkinter.Tk()

top.title("百通先控制台")
top.geometry('1024x800')

top.rowconfigure(0, weight=2)
top.rowconfigure(1, weight=2)
top.rowconfigure(2, weight=2)

top.columnconfigure(0, weight=2)
top.columnconfigure(1, weight=2)
top.columnconfigure(2, weight=2)
top.columnconfigure(3, weight=2)
top.columnconfigure(4, weight=2)

'''
top = Tkinter.Frame(tk, borderwidth=2)
top.grid()
'''

ict = Tkinter.Button(top, text = "ICT机")
ict.grid(row=1, column=0, padx=2, pady=2)
ict.display_name = "ICT机"

yz1 = Tkinter.Button(top, text = "移栽机1")
yz1.grid(row=0, column=1, padx=2, pady=2, rowspan=2,sticky='ns')
yz1.display_name = "移栽机1"

ft1 = Tkinter.Button(top, text = "FT机1")
ft1.grid(row=1, column=2, padx=2, pady=2, sticky='ew')
ft1.display_name = "FT机1"

ft2 = Tkinter.Button(top, text = "FT机2")
ft2.grid(row=0, column=2, padx=2, pady=2, sticky='ew')
ft2.display_name = "FT机2"

yz2 = Tkinter.Button(top, text = "移栽机2")
yz2.grid(row=0, column=3, padx=2, pady=2, rowspan=2,sticky='ns')
yz2.display_name = "移栽机2"

sbjng = Tkinter.Button(top, text = "NG收板机")
sbjng.grid(row=0, column=4, padx=2, pady=2)
sbjng.display_name = "NG收板机"

msg = Tkinter.Button(top, text="sendmsg", command=Device.sendmsg, bg="red", fg="white")
msg.grid(row=2, column=4, padx=2, pady=2)


def update_gui():
	writeDebug("update_gui is starting")
	#You check the status of devices every second
	time.sleep(1)
	while True:
		writeDebug("status is being checked")

		status = Device.device_ict.status
		device = ict
		device.config(text="%s %s"%(device.display_name, Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))

		status = Device.device_yz1.status
		device = yz1
		device.config(text="%s %s"%(device.display_name, Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))
		
		status = Device.device_ft1.status
		device =ft1
		device.config(text="%s %s"%(device.display_name, Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))
		
		status = Device.device_ft2.status
		device = ft2
		device.config(text="%s %s"%(device.display_name, Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))
		
		status = Device.device_yz2.status
		device = yz2
		device.config(text="%s %s"%(device.display_name, Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))
		

		status = Device.device_sbjng.status
		device = sbjng
		device.config(text="%s %s"%(device.display_name, Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))

		time.sleep(0.5)

def start_gui():
	writeDebug("GUI is starting")
	
	Tkinter.mainloop()
