# -*- coding: utf-8 -*-
#!/usr/bin/env python 

import time

#from socket import *
#setdefaulttimeout(3)

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 10002
CLIENT_HOST = '127.0.0.1'
CLIENT_PORT = 10003





IST_HANDSHAKE = "51 c0 00 11"
"51 0x xx crc"
"51 c0 01 12"
DEVICE_SENDITEM = "51 c1 00 12"
"51 c1 01 13"
"51 c1 02 14"
"51 c1 03 15"
HUANCUNJI_GETITEM_OK = "51 c2 00 13"
HUANCUNJI_GETITEM_NG = "51 c2 10 23"
"51 c2 01 14"
YIZAI_GETITEM_LEFT = "51 c2 02 15"
YIZAI_GETITEM_RIGHT = "51 c2 03 16"
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

# status sent from device
STATUS_AVAILABLE = "52 c4 01 17"			# 空闲 AVAILABLE
STATUS_GETITEM_FINISHED = "52 c4 02 18"		# 接板完成（等待状态） WAITING
STATUS_TESTING = "52 c4 03 19"				# 测试中 TESTING
STATUS_BROKEN = "52 c4 04 1a"				# 故障报警（故障状态） BROKEN
STATUS_READYFOR_SENDITEM = "52 c4 05 1b"	# 测试完成准备送板/准备好了送板（等待状态） WAITING
STATUS_SENDITEM_FINISHED = "52 c4 06 1c"	# 送板完成（空闲状态） AVAILABLE
STATUS_BUSY = "52 c4 07 1d"					# 忙碌 BUSY

# status in server
AVAILABLE = 0		# 空闲
WAITING = 1			# 测试/接板 完成，等待下一个设备空闲
TESTING = 2			# 测试中
BROKEN = 3			# 故障状态
BUSY = 4			# 忙碌



JBT0_IP = "10.0.0.100"
ICT_IP = "10.0.0.101"
HCJ_IP = "10.0.0.102"
JBT1_IP = "10.0.0.103"
FT_IP = "10.0.0.104"
YZ_IP = "10.0.0.105"
NGSBJ_IP = "10.0.0.106"
OKSBJ_IP = "10.0.0.107"

class Device:
	def __init__(self, name, ip):
		self.name = name
		self.ip = ip
		self.status = STATUS_AVAILABLE;

def Connect(first, second):
	if(first):
		first.next = second;
	if(second):
		second.previous = first;
		
device_jbt0 = Device("Jiebotai0", JBT0_IP)
device_ict = Device("ict", ICT_IP)
device_hcj = Device("hcj", HCJ_IP)
device_jbt1 = Device("jbt1", JBT1_IP)
device_ft = Device("ft", FT_IP)
device_yz = Device("yz", YZ_IP)
device_ngsbj = Device("ngsbj", NGSBJ_IP)
device_oksbj = Device("oksbj", OKSBJ_IP)

IP_Device_Map={}
IP_Device_Map[JBT0_IP] = device_jbt0
IP_Device_Map[ICT_IP] = device_ict
IP_Device_Map[HCJ_IP] = device_hcj
IP_Device_Map[FT_IP] = device_ft
IP_Device_Map[YZ_IP] = device_yz
IP_Device_Map[NGSBJ_IP] = device_ngsbj
IP_Device_Map[OKSBJ_IP] = device_oksbj

def getDeviceByIP(ip):
	print "IP is %s"%ip
	if(not ip in IP_Device_Map):
		return None
	return IP_Device_Map[ip]