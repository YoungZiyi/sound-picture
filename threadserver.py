# -*- coding: utf-8 -*-

import SocketServer 
import thread
import socket
import time
from bxtcommon import *
import string
from struct import pack, unpack
from array import array


class MyRequestHandler(SocketServer.BaseRequestHandler): 
	def handle(self):
		print 'Connected from ', self.client_address
		while 1:
			event = self.request.recv(1024)
			client_address = self.client_address
			client_ip = client_address[0]
			client_port = client_address[1]
			
			if(client_ip == "127.0.0.1"):
				#The localhost client is debugging, 
				#Use the ip address specified in the msg header
				ip_in_bytes = event[:4]
				ip_in_str = socket.inet_ntoa(ip_in_bytes)
				client_ip = ip_in_str
				event = event[4:]
			print "recv [%s] from [%s] \t"% (event, client_ip)
			
			#Get the device object to this IP address
			current_device = getDeviceByIP(client_ip)
			if(not current_device):
				print "No valid device to this address [%s]"%client_ip
				continue
			previous_device = current_device.previous
			if(event == None):
				print "No valid msg from this address [%s]"%client_ip
				continue
			if(event == "reset"):
				print "Command [reset] is received"
				self.server.shutdown()
				break


			# 握手反馈
			if (event == EVENT_SHAKEHANDS_RES):
				# 当前设备握手正常
				# 调宽反馈
				pass
			elif (event == EVENT_SETWIDTH_RES):
				# 当前设备调宽正常
				# 复位后返回当前状态
				pass
			elif (event == STATUS_AVAILABLE):
				# 当前设备空闲
				current_device.status = AVAILABLE
			elif (event == STATUS_GETITEM_FINISHED):
				# 当前设备接板完成（忙碌）
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
			# 空闲/正常
			elif (event == EVENT_AVAILABLE):
				# 当前设备空闲/正常
				current_device.status = AVAILABLE
			# 接板完成
			elif (event == EVENT_GETITEM_FINISHED):
				# 如果是接驳台，那就看系一个设备的状态，如果下一个设备的状态为AVAILABLE，就给当前设备发一个设备向前送板指令
				# 如果是ICT/FT测试设备，就将当前设备状态设为TESTING（不对！如果是测试设备，那设备开始测试的时候会发一条测试中的指令！）
				# 		那么要是是测试设备发送该指令作何处理呢？首先，测试设备接板完成后到测试中间会有一段间隙（必然），这段间隙中的设备状态应当设为忙碌，然后设备会自动开始测试，一旦开始测试，设备就会发送测试中指令给服务器，我们再将它的状态设为TESTING，直到它测试完成发其他指令
				# 缓存机有单独的接板完成指令
				# 如果是移载
				# 结论：识别设备，做出相应的反馈
				# 问题：如何识别设备（根据ip地址）
				if (current_device == device_jbt0 or current_device == device_jbt1):
					current_device.status = WAITING
					if (next_device.stauts == AVAILABLE):
						response = DEVICE_SENDITEM
					else:
						current_device.status = WAITING
				elif (current_device == device_ict):
					current_device.status = TESTING
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
	


	InitDeviceList()
	
	print 'To start TCPServer'
	ADDR = (SERVER_HOST, SERVER_PORT)
	tcpServ = SocketServer.ThreadingTCPServer(ADDR, MyRequestHandler) 
	print 'Waiting for connection'
	tcpServ.serve_forever()
	
	print "I am quitting"
	tcpServ.server_close()
	
