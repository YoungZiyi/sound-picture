# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import Qt
from PyQt4 import *
from spiderman import *
import sys
from threading import *
import socket
import time
from struct import pack, unpack
import signal
import binascii
import string
import select


from Message import *
from Device import *
from BxtLogger import *
from BxtException import *
from RunningMode import *



device_socket_map = {}
readlist = []
exceptionlist = []
	
def getDeviceNameBySocket(sock):
	for name in device_socket_map.keys():
		if(device_socket_map[name]) == sock:
			return name
	return None
	
def getSocketByDeviceName(name):
	if(name in device_socket_map):
		return device_socket_map[name]
	return None
	

def InitSockets():
	ADDR = (SERVER_HOST, SERVER_PORT)
	BUFSIZ = 16

	for deviceName in ["JBT0","ICT", "HCJ", "FT", "YZ", "SBJOK", "SBJNG" ]:
		print deviceName, " connecting..."
		tcpCliSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		tcpCliSock.connect(ADDR)
		print "Recving..."
		recved = tcpCliSock.recv(BUFSIZ)
		print "Recv ", recved.strip()
		
		data = getIPByDeviceName(deviceName)
		ip_in_str = socket.inet_aton(data)
		ip_in_int = unpack("!I", ip_in_str)[0];
		ip_in_binary_str = pack("!i",ip_in_int)

		msg = ip_in_binary_str + binascii.unhexlify(RemoveBlankInMiddle(EVENT_AVAILABLE))
		print "Msg is ", binascii.hexlify(msg)
		tcpCliSock.send(msg)
		device_socket_map[deviceName] = tcpCliSock
		#select监听这个socket
		readlist.append(tcpCliSock)
		exceptionlist.append(tcpCliSock)		
		
def ListenFromServer(x):
	print x;
	while 1:
		(sread, swrite, sexc) =  select.select(readlist, [], exceptionlist, 1); 
		for sock in sread:
			recv_buff = sock.recv(4)
			deviceName = getDeviceNameBySocket(sock)
			if(not verifyPacket(recv_buff)):
				print "WARN: Invalid Packet to [%s]" % (deviceName)
				continue
			hex_msg = ' '.join(x.encode('hex') for x in recv_buff)
			print "[%s] sent to [%s] "% (hex_msg, deviceName)
		
class ExampleApp(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(ExampleApp, self).__init__(parent)
		self.setupUi(self)

	def send_msg_to_server(self):
		objectName = str(self.sender().objectName())

		deviceNameInStr = objectName.split('_', 1)[0]
		variableNameInStr = objectName.split('_', 1)[1]
		
		msg = globals()[variableNameInStr]
		print deviceNameInStr, "#", msg
		
		ip = deviceName_IP_Map[deviceNameInStr]
		ip2 = socket.inet_aton(ip)
		ip_in_int = unpack("!I", ip2)[0];
		ip_in_binary_str = pack("!i",ip_in_int)
		
		msg = ip_in_binary_str + binascii.unhexlify(RemoveBlankInMiddle(msg))
		
		sock = getSocketByDeviceName(deviceNameInStr)
		sock.send(msg)

def thread_recv_msg_from_server(qlabel):
	print "communication thread is up"

	while 1:
		try:
			conn, addr = s.accept()
			print 'connected by:', addr
			data = conn.recv(2048)
			print "recv:\t", data
			conn.close();
			qlabel.setText(data)
		except Exception, e:
			print "thread_recv_msg_from_server"
			print e

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	form = ExampleApp()
	form.show()
	InitSockets()
	t = Thread(target=ListenFromServer, args = (form.log, ))
	t.daemon = True
	t.start()

	app.exec_()