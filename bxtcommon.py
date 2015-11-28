import socket
import time
socket.setdefaulttimeout(3)

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 10002
CLIENT_HOST = '127.0.0.1'
CLIENT_PORT = 10003

def sendToPeer(ip, port, content):
	try:
		theSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		theSocket.connect((ip, port))
		theSocket.sendall(content)
		print "DEBUG send:\t", content
		time.sleep(1)
	except Exception, e:
		print e," in sendToPeer"

def listenOn(ip, port):
	listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listenSocket.bind((ip, port))
	listenSocket.listen(1)
	return listenSocket

def recvFromPeer(listenSocket):
	response = None
	try:
		conn, addr = listenSocket.accept()	
		print 'DEBUG\tconnected by:', addr
		response = conn.recv(2048)
		print 'DEBUG\trecv:', response
	except Exception, e:
		print e," in recvFromPeer"
	return response

class Device:
	def __init__(self, name):
		self.name = name
		self.item = None
	def pushItem(self, item):
		self.item = item
	def popItem(self):
		i = self.item
		self.item = None
		return i
	def peekItem(self):
		return self.item

class Item:
	def __init__(self, name, status):
		self.name = name
		self.status = status