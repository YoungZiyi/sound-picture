# -*- coding: utf-8 -*-
#!/usr/bin/env python

import socket
import select
from struct import pack, unpack
import signal
import pdb

from Message import *
from Device import *
from BxtException import *
from MessageHandler import *
import RunnningMode

if __name__ == "__main__":
	signal.signal(signal.SIGINT, RunningMode.signal_handler)
	main()
	
def main():
	listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listenSock.bind(("", SERVER_PORT))
	listenSock.listen(15)
	listenSock.setblocking(1)
	#TODO  此处要设置默认socket超时时间

	readlist = [listenSock]
	exceptionlist = [listenSock]
	while not RunningMode.flag_exit:
		(sread, swrite, sexc) =  select.select(readlist, [], [], 1); 
		#TODO 此处可以加上定时任务.
		
		for sock in sread:
			try:
				if sock == listenSock:
					#收到一个新的TCP连接请求
					(newsock, address) = listenSock.accept()
					newsock.setblocking(1)
					print "ACCEPT a connection from ", address
					client_ip = address[0]
					client_port = address[1]
					#马上发送一个复位指令
					newsock.send(INSTRUCTION_DEVICE_RESET)
					#此处假定一次能收到整个包, 基本是成立的
					buff = newsock.recv(4)
					#如果处于debugging模式，则socket客户端会发送一个IP地址， 以替换127.0.0.1
					if(RunningMode.debugging):
						hex_msg = ':'.join(x.encode('hex') for x in buff)
						print hex_msg
						client_ip = socket.inet_ntoa(buff)
					current_device = getDeviceByIP(client_ip)
					if(not current_device):
						print "No valid device to this address [%s]"%client_ip
						newsock.close()
						continue
					else:
						current_device.sock = newsock
						readlist.append(newsock)
						exceptionlist.append(newsock)
						print "Accept socket for device ", current_device.name
				else:
					#业务socket发送的消息
					device = getDeviceBySocket(sock)
					if(not device):
						raise ExceptionMessageFromUnknonwSource(sock.getpeername())
					recv_msg = sock.recv(8)
					if recv_msg == "":
						print "Client %s closed the connection" % (device.name)
						current_device.sock = None
						
						readlist.remove(sock)
						exceptionlist.remove(sock)
						sock.close()
					else:
						hex_msg = ' '.join(x.encode('hex') for x in recv_msg)
						print "Client %s sent: [%s] "% (device.name, hex_msg)
						handle_msg(device, hex_msg)
			except Exception as e:
				print e

		for sock in sexc:
			try:
				if sock == listenSock:
					#TODO 此处应该把详细的error code打印出来以便日后debug
					print "Too bad, the listen socket is broken"
					RunningMode.flag_exit = True
				else:
					#TODO 此处应该把详细的error code打印出来以便日后debug
					print "socket ", sock, "is broken "
					sock.close()
					readlist.remove(sock)
					exceptionlist.remove(sock)
			except Exception as e:
				print e
			


				