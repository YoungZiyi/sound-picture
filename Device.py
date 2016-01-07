# -*- coding: utf-8 -*-
#!/usr/bin/env python 
import time
from Message import *

JBT0_IP = "192.168.0.101"
ICT_IP = "192.168.0.102"
HCJ_IP = "192.168.0.103"
JBT1_IP = "10.0.0.103"
FT_IP = "192.168.0.104"
YZ_IP = "192.168.0.105"
SBJNG_IP = "192.168.0.106"
SBJOK_IP = "192.168.0.107"

deviceName_IP_Map = {}
deviceName_IP_Map["JBT0"] = "192.168.0.101"
deviceName_IP_Map["ICT"] = "192.168.0.102"
deviceName_IP_Map["HCJ"] = "192.168.0.103"
deviceName_IP_Map["JBT1"] = "10.0.0.103"
deviceName_IP_Map["FT"] = "192.168.0.104"
deviceName_IP_Map["YZ"] = "192.168.0.105"
deviceName_IP_Map["SBJNG"] = "192.168.0.106"
deviceName_IP_Map["SBJOK"] = "192.168.0.107"

def getIPByDeviceName(deviceName):
	return deviceName_IP_Map[deviceName]

class Device:
	#TODO
	'''
		需要一个 toString() 方法, 打印该设备的所有信息
	'''
	
	def __str__(self):
		#TODO
		return "Device: %s, status:%d" %(self.name, self.status)
		
	def __init__(self, name, ip):
		self.name = name
		self.ip = ip
		self.Reset()

	def Reset(self):
		self.sock = None
		self.previous = None
		self.next = None
		self.status = S_RESETTING		#TODO 什么时候才能让Device可用? 还是一开始就可用?
		self.status_start_time = time.time()
		self.item_status = ITEM_STATUS_UNKNOWN
		self.prepare_count = 0	
		
	def ChangeStatusTo(self, status):
		self.status = status
		self.status_start_time = time.time()
		if(self.status == S_READY_TO_RECV_ITEM):
			#TODO why?
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
	
	def SendInstructionSendItem(self):
		cmd = INSTRUCTION_DEVICE_SENDITEM
		if(self == device_yz):
			#移栽机的送板指令不一样, 根据板子的状态来的
			if(self.item_status == ITEM_STATUS_OK):
				cmd = INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM
			else:
				cmd = INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM
		if(self.next):
			#如果当前设备不是最后一个机器(此处为移栽机), 则需要设置接板机的状态
			self.next.ChangeStatusTo(S_RECVING)
		self.ChangeStatusTo(S_SENDING)
		#TODO 这个时候就开始传递Item的状态, 是不是太早了?
		if(self.next):
			self.next.ChangeItemStatusTo(self.item_status)
		self.ChangeItemStatusTo(ITEM_STATUS_UNKNOWN)
		
	def SendInstructionPrepareToRecvItem(self):
		if(self == device_yz):
			_SendInstruction(INSTRUCTION_YZ_MOVE_LEFT_AND_RECV_ITEM)
		elif(self == device_hcj):
			cmd = INSTRUCTION_HCJ_RECV_ITEM_NG
			if(self.previous.item_status == ITEM_STATUS_OK):
				cmd = INSTRUCTION_HCJ_RECV_ITEM_OK
			_SendInstruction(cmd)
		#注意对于移栽机来说, 可能连续两次调用本函数分别达到S_HALF_READY_TO_RECV_ITEM, S_READY_TO_RECV_ITEM状态
		self.status = S_PREPARING_TO_RECV
		self.prepare_count = self.prepare_count +1
		
		
def Connect(first, second):
	if(first):
		first.next = second;
	if(second):
		second.previous = first;
		
#这里开始我们定义所有机器, 并放到IP_Device_Map中
device_jbt0 = Device("Jiebotai0", JBT0_IP)
device_ict = Device("ict", ICT_IP)
device_hcj = Device("hcj", HCJ_IP)
device_ft = Device("ft", FT_IP)
device_yz = Device("yz", YZ_IP)
device_sbjng = Device("ngsbj", SBJNG_IP)
device_sbjok = Device("oksbj", SBJOK_IP)

IP_Device_Map={}
IP_Device_Map[JBT0_IP] = device_jbt0
IP_Device_Map[ICT_IP] = device_ict
IP_Device_Map[HCJ_IP] = device_hcj
IP_Device_Map[FT_IP] = device_ft
IP_Device_Map[YZ_IP] = device_yz
IP_Device_Map[SBJNG_IP] = device_sbjng
IP_Device_Map[SBJOK_IP] = device_sbjok

Connect(None, device_jbt0)
Connect(device_jbt0, device_ict)
Connect(device_ict, device_hcj)
Connect(device_hcj, device_ft)
Connect(device_ft, device_yz)
Connect(device_yz, None)
#由于有两个接板机, 此处把移栽机的下位机设置为None, 避免混淆
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


