# -*- coding: utf-8 -*-

import SocketServer 
import thread
import socket
import time
from bxtcommon import *
import string

class MyRequestHandler(SocketServer.BaseRequestHandler): 
	def handle(self):
		print 'Connected from ', self.client_address
		while 1:
			event = self.request.recv(1024)
			event = string.strip(event, "\r\n")
			print "recvFrom %s [%s]\t"%(self.client_address, event)
			if(event == None):
				continue
			if(event == "reset"):
				self.server.shutdown()
			else:
				response = "UNKNOWN MESSAGE: "
				response += event
			self.request.sendall(response)

def InitDeviceList():
	Connect(None, device_jbt0)
	Connect(device_jbt0, device_ict)
	Connect(device_ict, device_hcj)
	Connect(device_hcj, device_jbt1)
	Connect(device_jbt1, device_ft)
	Connect(device_ft, device_yz)
	Connect(device_yz, device_ngsbj)
	Connect(device_yz, device_oksbj)
	Connect(device_ngsbj, None)
	Connect(device_oksbj, None)


if __name__ == "__main__":
	print 'To define global variables'
	
	device_jbt0 = Device("Jiebotai0", JBT0_IP)
	device_ict = Device("ict", ICT_IP)
	device_hcj = Device("hcj", HCJ_IP)
	device_jbt1 = Device("jbt1", JBT1_IP)
	device_ft = Device("ft", FT_IP)
	device_yz = Device("yz", YZ_IP)
	device_ngsbj = Device("ngsbj", NGSBJ_IP)
	device_oksbj = Device("oksbj", OKSBJ_IP)

	InitDeviceList()
	
	print 'To start TCPServer'
	ADDR = (SERVER_HOST, SERVER_PORT)
	tcpServ = SocketServer.ThreadingTCPServer(ADDR, MyRequestHandler) 
	print 'Waiting for connection'
	tcpServ.serve_forever()
	
	print "I am quitting"
	tcpServ.server_close()
	