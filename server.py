# -*- coding: utf-8 -*-

import socket
import time
from bxtcommon import *


device_jbt0 = Device("Jiebotai0", JBT0_IP)
device_ict = Device("ict", ICT_IP)
device_hcj = Device("hcj", HCJ_IP)
device_jbt1 = Device("jbt1", JBT1_IP)
device_ft = Device("ft", FT_IP)
device_yz = Device("yz", YZ_IP)
device_ngsbj = Device("ngsbj", NGSBJ_IP)
device_oksbj = Device("oksbj", OKSBJ_IP)

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

			remote_ip = getIpFromsocket();
			current_device = getDeviceByIP(remote_ip)
			# 握手反馈
			if (event == EVENT_SHAKEHANDS_RES):
				current_device.status = STATUS_AVAILABLE
			# 调宽反馈
			elif (event == EVENT_SETWIDTH_RES):
				current_device.status = STATUS_AVAILABLE
			# 复位后返回当前状态
			elif (event == EVENT_RESET_STATUS_RES):
				current_device.status = STATUS_AVAILABLE
			# 空闲/正常 or 送板完成
			elif(event == EVENT_AVAILABLE or event == EVENT_COMMON_AVAILABLE or event == EVENT_COMMON_SENDITEM_FINISHED or event == EVENT_SENDITEM_FINISHED)
				current_device.status = STATUS_AVAILABLE;
				previous_device = current_device.previous;
				if(previous_device.status == STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE):
					sendToPeer(previous_device, IST_SENDITEM)
					previous_device.status = STATUS_SENDING
					current_device.status = STATUS_RECVING
			# 接板完成
			elif (event == EVENT_GETITEM_FINISHED):
				current_device.status = STATUS_BUSY
			# 缓存机接板完成
			elif (event == EVENT_HUANCUNJI_GETITEM_FINISHED):
				current_device.status = STATUS_BUSY
			# 准备好接OK板
			elif (event == EVENT_READYFOR_GETITEM_OK):
				current_device.status = STATUS_AVAILABLE
				previous_device = current_device.previous
			# 准备好接NG板
			# 缓存机接板忙
			# 缓存机接板故障
			# 已到达中间准备好接板
			# 已到达左端准备好接板
			# 已到达右端准备好接板
			# 测试中

			
			# 测试OK，准备送板
			elif (event == EVENT_READYFOR_SENDITEM_OK):
				next_device = current_device.next
				if(next_device.status == STATUS_AVAILABLE):
					sendToPeer(current_device, HUANCUNJI_GETITEM_OK)
				else:
					current_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			# 测试NG，准备送板
			elif (event == EVENT_READYFOR_SENDITEM_NG):
				next_device = current_device.next
				if(next_device.status == STATUS_AVAILABLE):
					sendToPeer(current_device, HUANCUNJI_GETITEM_NG)
				else:
					current_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE
			

			# 准备送板
			elif (event == EVENT_COMMON_READYFOR_SENDITEM):
				next_device = current_device.next
				if(next_device.status == STATUS_AVAILABLE):
					sendToPeer(current_device, IST_SENDITEM)
					current_device.status = STATUS_SENDING
					next_device.status = STATUS_RECVING
				else:
					current_device.status = STATUS_WAITING_FOR_NEXT_DEVICE_TO_BE_AVAILABLE



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