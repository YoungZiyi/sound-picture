import socket
import time
socket.setdefaulttimeout(3)

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 10002
CLIENT_HOST = '127.0.0.1'
CLIENT_PORT = 10003


JBT0_IP = "10.0.0.100"
ICT_IP = "10.0.0.101"

IST_HANDSHAKE = "51 c0 00 11"
"51 0x xx crc"
"51 c0 01 12"
IST_SENDITEM = "51 c1 00 12"
"51 c1 01 13"
"51 c1 02 14"
"51 c1 03 15"
"51 c2 00 13"
"51 c2 10 23"
"51 c2 01 14"
"51 c2 02 15"
"51 c2 03 16"
"51 c4 00 15"



EVENT_SHAKEHANDS_RES = "52 c0 00 12"
EVENT_SETWIDTH_RES = "52 0x xx crc"
EVENT_RESET_STATUS_RES = "52 0x xx crc"
EVENT_AVAILABLE = "52 c1 f0 03"
EVENT_GETITEM_FINISHED = "52 c1 f1 04"
EVENT_SENDITEM_FINISHED = "52 c1 f2 05"
EVENT_HUANCUNJI_GETITEM_FINISHED = "52 c2 00 14"
EVENT_READYFOR_GETITEM_OK = "52 c3 04 19"
EVENT_READYFOR_GETITEM_NG = "52 c3 05 1a"
EVENT_HUANCUNJI_BUSY = "52 c3 06 1b"
EVENT_HUANCUNJI_GETITEM_ERROR = "52 c3 07 1c"
EVENT_READYFOR_GETITEM_MIDDLE = "52 c2 01 15"
EVENT_READYFOR_GETITEM_LEFT = "52 c2 02 16"
EVENT_READYFOR_GETITEM_RIGHT = "52 c2 03 17"
EVENT_TESTING = "52 c1 f3 06"
EVENT_READYFOR_SENDITEM_OK = "52 c1 f4 07"
EVENT_READYFOR_SENDITEN_NG = "52 c1 f5 08"
EVENT_READYFOR_SENDITEM = "52 c1 f6 09"
EVENT_DEVICE_WARNING_1 = "52 c3 xx crc"
EVENT_DEVICE_WARNING_2 = "52 c3 00 15"
EVENT_DEVICE_WARNING_3 = "52 c3 01 16"
EVENT_DEVICE_WARNING_4 = "52 c3 02 17"
EVENT_HUANCUNJI_NOTREADY = "52 c3 03 18"

# device common status
EVENT_COMMON_AVAILABLE = "52 c4 01 17"
EVENT_COMMON_GETITEM_FINISHED = "52 c4 02 18"
EVENT_COMMON_TESTING = "52 c4 03 19"
EVENT_COMMON_WARNING = "52 c4 04 1a"
EVENT_COMMON_READYFOR_SENDITEM = "52 c4 05 1b"
EVENT_COMMON_SENDITEM_FINISHED = "52 c4 06 1c"
EVENT_COMMON_BUSY = "52 c4 07 1d"

STATUS_AVAILABLE = 0;
STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE= 2;
STATUS_BUSY = 3;
STATUS_BROKEN = 4;
STATUS_RECVING = 5;
STATUS_SENDING = 6;



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
	def __init__(self, name, ip):
		self.name = name
		self.ip = ip
		self.status = AVAILABLE;

def Connect(first, second):
	if(first):
		first.next = second;
	if(second != None):
		second.previous = first;