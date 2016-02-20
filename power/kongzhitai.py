import Tkinter
from BxtLogger import *
import Device
import time
from Tkconstants import *
import Device

tk = Tkinter.Tk()

top = Tkinter.Frame(tk, borderwidth=2)
top.pack(fill=BOTH, expand=1)

ict = Tkinter.Label(top, text = "ict", fg="red")
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
	color_on = False
	writeDebug("update_gui is starting")
	#You check the status of devices every second
	time.sleep(1)
	while True:
		writeDebug("status is being checked")
		status =Device.device_ict.status
		ict.config(text="%s"%(Device.status_name_map[status]))
		color_on = False
		time.sleep(1)

def start_gui():
	writeDebug("GUI is starting")
	
	Tkinter.mainloop()

