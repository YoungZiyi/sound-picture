# -*- coding: utf-8 -*-

import socket
import time
from bxtcommon import *

ft01 = Device("FT01")
yizai = Device("YIZAI")


def main():
	count = 0
	listenSocket = listenOn(SERVER_HOST, SERVER_PORT)

	print 'Running...'
	while 1:
		try:
			event = recvFromPeer(listenSocket)
			print "recvFromPeer\t", event
			if(event == None):
				continue
			if(event == "reset"):
				break
			if ('FT01_TestFinish' in event):
				count += 1
				oldItem = ft01.peekItem()
				if(oldItem != None):
					sendToPeer(CLIENT_HOST, CLIENT_PORT, "FT01_HasTwoItems!")
					continue;

				newItem = Item("Item:"+str(count), "")
				if("OK" in event):
					newItem.status = "OK"
				elif("NG" in event):
					newItem.status = "NG"
				else:
					sendToPeer(CLIENT_HOST, CLIENT_PORT, "FT01_ItemInWrongStatus!")
					continue;	
				#Put a new item with FT01
				ft01.pushItem(newItem)
				response = "YIZAI_Move_LEFT"
			elif ("YIZAI_MoveFinish" in event):
				item = yizai.peekItem()
				if(item == None):
					response = "YIZAI_PrepareGetItem"
				elif(item.status == "OK"):
					response = "OKSBJ_PrepareGetItem"
				elif(item.status == "NG"):
					response = "NGSBJ_PrepareGetItem"	
			elif event == "YIZAI_PrepareGetItemFinish":
				response = "FT01_GiveItem"
			elif event == "FT01_GiveItemFinish":
				item = ft01.popItem()
				yizai.pushItem(item)
				#Here we should check if thers is a item with the ft01
				if(item.status == "OK"):
					response = "YIZAI_Move_LEFT"
				else:
					response = "YIZAI_Move_RIGHT"
			elif ("SBJ_PrepareGetItemFinish" in event):
				response = "YIZAI_GiveItem"
			
			else:
				response = "UNKNOWN MESSAGE: "
				response += event

			sendToPeer(CLIENT_HOST, CLIENT_PORT, response)
		except Exception, e:
			print "[",e, "]"

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
			print "KeyboardInterrupt"
	finally:
		print "finally"
	
	print "I am quitting"