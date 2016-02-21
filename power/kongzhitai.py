# -*- coding: utf-8 -*-
#!/usr/bin/env python

import Tkinter
from BxtLogger import *
import Device
import time
from Tkconstants import *
import Device

tk = Tkinter.Tk()

top = Tkinter.Frame(tk, borderwidth=2)
top.pack(fill=BOTH, expand=1)

ict = Tkinter.Label(top, text = "ict")
ict.pack()

yz1 = Tkinter.Label(top, text = "yz1")
yz1.pack()

ft1 = Tkinter.Label(top, text = "ft1")
ft1.pack()

ft2 = Tkinter.Label(top, text = "ft2")
ft2.pack()

yz2 = Tkinter.Label(top, text = "yz2")
yz2.pack()

sbjng = Tkinter.Label(top, text = "sbjng")
sbjng.pack()

msg = Tkinter.Button(top, text="sendmsg", command=Device.sendmsg, bg="red", fg="white")
msg.pack()


def update_gui():
	writeDebug("update_gui is starting")
	#You check the status of devices every second
	time.sleep(1)
	while True:
		writeDebug("status is being checked")

		status = Device.device_ict.status
		ict.config(text="%s"%(Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))

		status = Device.device_yz1.status
		yz1.config(text="%s"%(Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))
		
		status = Device.device_ft1.status
		ft1.config(text="%s"%(Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))
		
		status = Device.device_ft2.status
		ft2.config(text="%s"%(Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))
		
		status = Device.device_yz2.status
		yz2.config(text="%s"%(Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))

		status = Device.device_sbjng.status
		sbjng.config(text="%s"%(Device.status_name_map_in_chinese[status]), fg="%s"%(Device.status_to_color[status]))

		time.sleep(0.5)

def start_gui():
	writeDebug("GUI is starting")
	
	Tkinter.mainloop()

