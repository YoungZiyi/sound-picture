# -*- coding: utf-8 -*-
#!/usr/bin/env python 
import time
from Message import *
from BxtException import *
from BxtLogger import *

ICT_IP = "192.168.0.102"
YZ1_IP = "192.168.0.103"
FT1_IP = "192.168.0.106"
FT2_IP = "192.168.0.107"
YZ2_IP = "192.168.0.108"
SBJNG_IP = "192.168.0.109"

deviceName_IP_Map = {}

deviceName_IP_Map["ICT"] = ICT_IP
deviceName_IP_Map["YZ1"] = YZ1_IP
deviceName_IP_Map["FT1"] = FT1_IP
deviceName_IP_Map["FT2"] = FT2_IP
deviceName_IP_Map["YZ2"] = YZ2_IP
deviceName_IP_Map["SBJNG"] = SBJNG_IP

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
		self.status = S_RESETTING		#TODO 什么时候才能让Device可用? 还是一开始就可用?
		self.status_start_time = time.time()
		self.item_status = ITEM_STATUS_NG
		self.direction = DIRECTION_UNKNOWN
		
	def ChangeStatusTo(self, status):
		self.status = status
		self.status_start_time = time.time()
		if(self.status in [S_READY_TO_RECV_ITEM, S_IDLE]):
			self.item_status = ITEM_STATUS_UNKNOWN
			self.direction = DIRECTION_UNKNOWN
		
	# ng is a bool value
	def ChangeItemStatusTo(self, status):
		self.item_status = status

	def _SendInstruction(self, instruction):
		if(not self.sock):
			writeWarning("Server sent to [%s]: [%s] FAILURE" % (self.name, GetInstructionName(instruction)))	
			raise ExceptionCommunication(self.name+" No sock")
		writeInfo("Server sent to [%s]: [%s]" % (self.name, GetInstructionName(instruction)))
		self.sock.send(convert2Hex(instruction))

	def SendInstruction(self, instruction):
		if(instruction in [INSTRUCTION_DEVICE_SENDITEM, INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM, INSTRUCTION_HCJ_RECV_ITEM_OK, INSTRUCTION_HCJ_RECV_ITEM_NG]):
			raise Exception("Please call the Specific SendInstrctionXXX")
		self._SendInstruction(instruction)

		
#这里开始我们定义所有机器, 并放到IP_Device_Map中

device_ict = Device("ict", ICT_IP)
device_yz1 = Device("yz1", YZ1_IP)
device_ft1 = Device("ft1", FT1_IP)
device_ft2 = Device("ft2", FT2_IP)
device_yz2 = Device("yz2", YZ2_IP)
device_sbjng = Device("sbjng", SBJNG_IP)


IP_Device_Map={}

IP_Device_Map[ICT_IP] = device_ict
IP_Device_Map[YZ1_IP] = device_yz1
IP_Device_Map[FT1_IP] = device_ft1
IP_Device_Map[FT2_IP] = device_ft2
IP_Device_Map[YZ2_IP] = device_yz2
IP_Device_Map[SBJNG_IP] = device_sbjng
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

def getIPBySocket(sock):
	for device in IP_Device_Map.values():
		if(device.ip == sock.getpeername()[0]):
			return device
	return None

def sendmsg():
	writeInfo("Msg received!")

def SetRailWidth(device_name, width):
	device = eval("device_" + device_name)
	SetWidth = hex(int(width/0.025))[2:]
	if(len(SetWidth) == 1):
		checknum = hex(0x51 + eval("0x" + SetWidth))[-2:]
		instruction = "51 00 0" + SetWidth + " " + checknum
	elif(len(SetWidth) == 2):
		checknum = hex(0x51 + eval("0x" + SetWidth))[-2:]
		instruction = "51 00 " + SetWidth + " " + checknum
	elif(len(SetWidth) == 3):
		checknum = hex(0x51 + eval("0x" + SetWidth[0:1]) + eval("0x" + SetWidth[2:]))[-2:]
		instruction = "51 0" + SetWidth[0:1] + " " + SetWidth[1:] + " " + checknum
	elif(len(SetWidth) == 4):
		checknum = hex(0x51 + eval("0x" + SetWidth[0:2]) + eval("0x" + SetWidth[2:]))[-2:]
		instruction = "51 " + SetWidth[0:2] + " " + SetWidth[2:] + " " + checknum
	else:
		writeError("Unable set width to " + width)
		raise ExceptionWidthOutOfRange
	writeInfo("%s set width to %smm instruction:%s"%(device_name, width, instruction))
	device._SendInstruction(instruction)