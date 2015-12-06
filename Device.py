# -*- coding: utf-8 -*-
#!/usr/bin/env python 
import time
from Message import *



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
		self.Reset()
		
	def Reset(self):
		self.sock = None
		self.status = S_AVAILABLE		#TODO 什么时候才能让Device可用? 还是一开始就可用?
		self.status_start_time = time.time()
		self.item_status = ITEM_STATUS_UNKNOWN
		self.prepare_count = 0	
		
	def ChangeStatusTo(self, status):
		self.status = status
		self.status_start_time = time.time()
		if(self.status == S_READY_TO_RECV_ITEM):
			self.prepare_count = 0

	# ng is a bool value
	def ChangeItemStatusTo(self, status):
		self.item_status = status

	def _SendInstruction(self, instruction):
		if(not self.sock):
			raise ExceptionCommunication(self.name+" No sock")
		self.sock.send(instruction)

	def SendInstruction(self, instruction):
		if(instruction in [INSTRUCTION_DEVICE_SENDITEM, INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM, INSTRUCTION_HCJ_RECV_ITEM_OK, INSTRUCTION_HCJ_RECV_ITEM_NG]):
			raise Exception("Please call the Specific SendInstrctionXXX")
		_SendInstruction(self, instruction)
	
	def SendInstructionSendItem(self, instruction):
		_SendInstruction(INSTRUCTION_DEVICE_SENDITEM)
		if(self != device_yz):
			#如果当前设备是移栽机, 则不用设置接板机的状态
			self.next.ChangeStatusTo(S_RECVING)
		self.ChangeStatusTo(S_SENDING)
		#TODO 这个时候就开始传递Item的状态, 是不是太早了?
		self.next.ChangeItemStatusTo(self.item_status)
		self.ChangeItemStatusTo(ITEM_STATUS_UNKNOWN)
		
	def SendInstructionPrepareToRecvItem(self):
		if(self == device_yz):
			_SendInstruction(INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM)
		elif(self == device_hcj):
			_SendInstruction(self.previous.item_status == ITEM_STATUS_OK ? INSTRUCTION_HCJ_RECV_ITEM_OK : INSTRUCTION_HCJ_RECV_ITEM_NG)
		#注意对于移栽机来说, 可能连续两次调用本函数分别达到S_HALF_READY_TO_RECV_ITEM, S_READY_TO_RECV_ITEM状态
		self.status = S_PREPARING_TO_RECV
		self.prepare_count = self.prepare_count +1
		
#这里开始我们定义所有机器, 并放到IP_Device_Map中
device_jbt0 = Device("Jiebotai0", JBT0_IP)
device_ict = Device("ict", ICT_IP)
device_hcj = Device("hcj", HCJ_IP)
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
