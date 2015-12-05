# -*- coding: utf-8 -*-


import socket
import select
import time
from bxtcommon import *
import string
from struct import pack, unpack
from array import array
import signal
import pdb

is_exit = False
def signal_handler(signum, frame):
	global is_exit
	is_exit = True
	print "receive a signal %d, is_exit = %d"%(signum, is_exit)
signal.signal(signal.SIGINT, signal_handler)

servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servsock.bind(("", SERVER_PORT))
servsock.listen(15)
servsock.setblocking(1)

readlist = [servsock]
exceptionlist = [servsock]
while not is_exit:
    (sread, swrite, sexc) =  select.select(readlist, [], [], 5); 

    for sock in sread:
        #received a connect to the server socket
        if  sock == servsock:
            (newsock, address) = servsock.accept()
            newsock.setblocking(1)
            print "ACCEPT a connection from ", address
            client_ip, client_port = newsock.getpeername()
            current_device = getDeviceByIP(client_ip)
			if(not current_device):
				print "No valid device to this address [%s]"%client_ip
				sock.close()
			else:
				current_device.sock = newsock
				readlist.append(newsock)
	            exceptionlist.append(newsock)
	            print "accept socket for device ", current_device.name
        else:
        	client_ip, client_port = sock.getpeername()
            recv_msg = sock.recv(4)
            if recv_msg == "":
                print "Client %s:%s closed the connection" % (client_ip, client_port)
                current_device = getDeviceByIP(client_ip)
                if(current_device):
                	current_device.sock = None
                readlist.remove(sock)
                sock.close()
            else:
            	hex_msg = ':'.join(x.encode('hex') for x in recv_msg)
                print "client %s sent: %s "% (client_ip, hex_msg)
                handle_msg(sock, recv_msg)
                #pdb.set_trace()

    for sock in sexc:
    	if sock == servsock:
    		print "Too bad, the listen socket is broken"
    		is_exit = True
    	else:
    		print "socket ", sock, "is broken"
    		sock.close()
    		readlist.remove(sock)
    		exceptionlist.remove(sock)


def send_instruction(device, instruction):
	if(not device.sock):
		print device.name, ERRCODE_DEVICE_IS_WITHOUT_SOCKET_WHILE_SENDING_INSTRUCTION
	sock.send(instruction)

def handle_msg(sock, event):
		client_ip, client_port = sock.getpeername()
		#Get the device object to this IP address
		current_device = getDeviceByIP(client_ip)
		if(not current_device):
			print "No valid device to this address [%s]"%client_ip
			return	
		previous_device = current_device.previous
		next_device = current_device.next
		# 握手反馈
		if(event == EVENT_AVAILABLE or event == STATUS_AVAILABLE or event == STATUS_SENDITEM_FINISHED or event == EVENT_SENDITEM_FINISHED):
			current_device.status = S_AVAILABLE
			#如果上一个设备在等待本设备， 此时我们可以开始上一个设备往本设备送板的动作了
			if(previous_device.status == S_WAITING):
				if(current_device == device_yz):
					#如果本设备是移栽机， 则需要先让移栽机移动到右边
					send_instruction(current_device, YIZAI_MOVE_RIGHT_AND_RECV_ITEM)
					current_device.status = S_MOVING
				elif(current_device == device_hcj):
					#如果本设备是缓存机，则需要先辨别上一个设备的板子是OK还是NG的， 以给本设备发送不同的指令
					if(previous_device.item_status == ITEM_STATUS_OK):
						send_instruction(current_device, INSTRUCTION_HUANCUNJI_GETITEM_OK)
						current_device.status = S_RECVING
					elif(previous_device.item_status == ITEM_STATUS_NG):
						send_instruction(current_device, INSTRUCTION_HUANCUNJI_GETITEM_NG)
						current_device.status = S_RECVING
					else:
						print "ERROR. Item status is unknow. [%d]" % ERRCODE_STATUS_OF_ITEM_IN_PREVIOUS_DEVICE_IS_UNKNOWN
						current_device.status = ERRCODE_STATUS_OF_ITEM_IN_PREVIOUS_DEVICE_IS_UNKNOWN
				else:
					#对于其他设备，让上一个设备直接送板
					send_instruction(previous_device, INSTRUCTION_DEVICE_SENDITEM)
					current_device.status = S_RECVING
		elif (event == EVENT_SHAKEHANDS_RES):
			# 当前设备握手正常
			pass
		elif (event == EVENT_SETWIDTH_RES):
			# 当前设备调宽正常
			pass
		elif (event == STATUS_AVAILABLE):
			# 当前设备空闲
			current_device.status = AVAILABLE
		elif (event == STATUS_GETITEM_FINISHED):
			# 如果是接驳台，那就看下一个设备的状态，如果下一个设备的状态为AVAILABLE，就给当前设备发一个设备向前送板指令
			# 缓存机有单独的接板完成指令
			# 如果是移载
			# 结论：识别设备，做出相应的反馈
			# 问题：如何识别设备（根据ip地址）
			# 当前设备接板完成（忙碌）
			current_device.status = 
			if(current_device == device_yz):
				if(current_device.item_status == ITEM_STATUS_NOT_KNOWN):
					Print "ERROR: 移载机上的板子状态未知， OK or NG？"
					return
				elif(current_device.item_status == ITEM_STATUS_OK):
					send_instruction(current_device, YIZAI_MOVE_RIGHT_AND_SEND_ITEM)
				else:
					send_instruction(current_device, YIZAI_MOVE_LEFT_AND_SEND_ITEM)
			current_device.status = WAITING
		elif (event == STATUS_TESTING):
			# 当前设备测试中
			current_device.status = TESTING
		elif (event == STATUS_BROKEN):
			# 当前设备处于故障状态
			current_device.status = BROKEN
		elif (event == STATUS_READYFOR_SENDITEM):
			# 当前设备测试完成准备送板
			current_device.status = WAITING
		elif (event == STATUS_SENDITEM_FINISHED):
			# 当前设备送板完成
			current_device.status = AVAILABLE
		elif (event == STATUS_BUSY):
			# 当前设备忙碌
			current_device.status = BUSY
		
		# 送板完成
		elif (event == EVENT_SENDITEM_FINISHED):
			# 当前设备送板完成
			if (current_device == device_jbt0 or current_device == device_jbt1):
				current_device.status = AVAILABLE
		# 缓存机接板完成/空闲
		elif (event == EVENT_HUANCUNJI_GETITEM_FINISHED):
			# 缓存机接板完成/空闲？难道说缓存机接板完成立即变成空闲状态？
			# 缓存机还有好多疑问，按顺序来应该走ICT，先空着这里
			# 准备好接OK板
			pass
		elif (event == EVENT_READYFOR_GETITEM_OK):
			pass
		# 准备好接NG板
		elif (event == EVENT_READYFOR_GETITEM_NG):
			pass
		# 缓存机接板忙
		elif (event == EVENT_HUANCUNJI_BUSY):
			pass
			# 怎么样才会触发缓存机发送该指令？
		# 缓存机故障
		elif (event == EVENT_HUANCUNJI_GETITEM_ERROR):
			# 缓存机故障
			current_device.status = BROKEN
		# 已到达中间准备好接板
		elif (event == EVENT_READYFOR_GETITEM_MIDDLE):
			# 这个指令时谁发的？移载？移载中间也可以接板？
			# 先不管它，根据协议乱来吧
			# 既然移载已经到达中间准备好接板了，首先给当前设备设个AVAILABLE状态
			curretn_device.status = AVAILABLE
		# 已到达左端准备好接板
		elif (event == EVENT_READYFOR_GETITEM_LEFT):
			# 同上
			current_device.status = AVAILABLE
		# 已到达右端准备好接板
		elif (event == EVENT_READYFOR_GETITEM_RIGHT):
			# 同上
			current_device.status = AVAILABLE
		# 测试中
		elif (event == EVENT_TESTING):
			# ICT/FT开始测试工作
			# 那么给它们设为TESTING状态
			current_device.status = TESTING
		# 测试OK，准备送板
		elif (event == EVENT_READYFOR_SENDITEM_OK):
			# 准备送OK板
			# 要明确通知下一个设备接OK板，并将当前和下一个设备状态设为BUSY
			if (next_device.status == AVAILABLE):
				sendToPeer(current_device, DEVICE_SENDITEM)
				current_device.status = BUSY
				if (next_device == device_hcj):
					sendToPeer(next_device, HUANCUNJI_GETITEM_OK)
				if (next_device == device_yz):
					sendToPeer(next_device, YIZAI_GETITEM_RIGHT)
				next_device.status = BUSY
		# 测试NG，准备送板
		elif (event == EVENT_READYFOR_SENDITEM_OK):
			# 准备送NG板
			# 要明确通知下一个设备接NG板，并将当前和下一个设备状态设为BUSY
			if (next_device.status == AVAILABLE):
				sendToPeer(current_device, DEVICE_SENDITEM)
				current_device.status = BUSY
				if (next_device == device_hcj):
					sendToPeer(next_device, HUANCUNJI_GETITEM_NG)
				if (next_device == device_yz):
					sendToPeer(next_device, YIZAI_GETITEM_RIGHT)
				next_device.status = BUSY
		# 准备送板（无测试）
		elif (event == EVENT_READYFOR_SENDITEM):
			pass
			# 无测试怎么通知后一个设备接板？
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_1):
			pass
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_2):
			pass
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_3):
			pass
		# 机台异常报警
		elif (event == EVENT_DEVICE_WARNING_4):
			pass
		# 缓存机未准备好
		elif (event == EVENT_HUANCUNJI_NOTREADY):
			pass
		else:
			response = "UNKNOWN MESSAGE: "
			response += event
		self.request.sendall(response)
                