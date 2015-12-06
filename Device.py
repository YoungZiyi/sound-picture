# -*- coding: utf-8 -*-
#!/usr/bin/env python 
import time
from Message import *

#最低8bit标识设备的状态
S_IDLE			=	0x0000	# 空闲
S_MOVING		=	0x0001	# 移栽机在移动中
S_RECVING		=	0x0002 	# 接板中
S_WITH_ITEM		=	0x0003	# 设备上有板子
S_TESTING		=	0x0004	# 测试中
S_WAITING		=	0x0005	# 测试/接板 完成，等待下一个设备空闲以便送版
S_SENDING		=	0x0006	# 送板中
S_BROKEN		=	0x0007	# 故障状态
S_RESETTING		=	0x0008	# 重启中
S_MASK			=	0x000F	# Mask
#最后一个标识代码逻辑有问题
S_UNKNOWN		=	0xFFFF	# 未知状态

#所携带的板子的状态
ITEM_STATUS_OKAY		=	0
ITEM_STATUS_NG			=	1
ITEM_STATUS_UNKNOWN		=	2
#ITEM_STATUS_NO_ITEM		=	3

def matchStatus(statusA, statusB):
	if(statusB <= S_MASK):
		return (statusA & S_MASK) == statusB
	return (statusA & statusB) != 0

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
		self.sock = None
		self.status = S_AVAILABLE
		self.status_start_time = time.time()
		self.item_status = ITEM_STATUS_UNKNOWN

	def ChangeStatusTo(self, status):
		self.status = status
		self.status_start_time = time.time()

	# ng is a bool value
	def ChangeItemStatusTo(self, status):
		self.item_status = status

	def SendInstruction(self, instruction):
		if(not self.sock):
			raise ExceptionCommunication(self.name+" No sock")
		self.sock.send(instruction)
		if(instruction == INSTRUCTION_DEVICE_SENDITEM):
			self.status = S_SENDING
	
#这里开始我们定义所有机器, 并放到IP_Device_Map中
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
#此处结束定义所有机器

def getDeviceByIP(ip):
	if(not ip in IP_Device_Map):
		return None
	return IP_Device_Map[ip]
	
def getDeviceBySocket(sock):
	for device in IP_Device_Map.values():
		if(device.sock == sock):
			return device
	return None
	

def Connect(first, second):
	if(first):
		first.next = second;
	if(second):
		second.previous = first;
