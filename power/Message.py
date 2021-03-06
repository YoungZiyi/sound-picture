# -*- coding: utf-8 -*-
#!/usr/bin/env python 

import string
from BxtLogger import *

SERVER_HOST = '198.168.0.11'
SERVER_PORT = 6001

#最低8bit标识设备的状态
S_IDLE							=	0x0000	# 空闲
S_PREPARING_TO_RECV				=	0x0001	# 移栽机在移动中
#S_HALF_READY_TO_RECV_ITEM		=	0x0002	# 移栽机已经到达接板位置, 但是需要再次确认其准备好了
S_READY_TO_RECV_ITEM 			=	0x0003 	# 准备好接板
S_RECVING						=	0x0004	# 接板中
S_WITH_ITEM						=	0x0005	# 设备上有板子    
S_TESTING						=	0x0006	# 测试中      
S_READY_TO_SEND_ITEM			=	0x0007	# 准备好送板
S_SENDING						=	0x0008	# 送板中    
S_BROKEN						=	0x0009	# 故障状态    
S_RESETTING						=	0x000A	# 重启中    
S_UNKNOWN						=	0xFFFF	# 未知状态

status_name_map = dict((eval(name), name) for name in ["S_IDLE", "S_PREPARING_TO_RECV", "S_READY_TO_RECV_ITEM", "S_RECVING", "S_WITH_ITEM", "S_TESTING", "S_READY_TO_SEND_ITEM", "S_SENDING", "S_BROKEN", "S_RESETTING", "S_UNKNOWN"])
status_name_map_in_chinese = {S_IDLE:"空闲", S_PREPARING_TO_RECV:"准备接板中", S_READY_TO_RECV_ITEM:"准备好接板", S_RECVING:"接板中", S_WITH_ITEM:"设备上有板", S_TESTING:"测试中", S_READY_TO_SEND_ITEM:"准备好送板", S_SENDING:"送板中", S_BROKEN:"设备故障", S_RESETTING:"复位中", S_UNKNOWN:"未知状态"}

status_to_color = {S_IDLE:"green", S_PREPARING_TO_RECV:"green", S_READY_TO_RECV_ITEM:"green", S_RECVING:"blue", S_WITH_ITEM:"blue", S_TESTING:"blue", S_READY_TO_SEND_ITEM:"blue", S_SENDING:"blue", S_BROKEN:"red", S_RESETTING:"blue", S_UNKNOWN:"black"}

#所携带的板子的状态
ITEM_STATUS_OK			=	0
ITEM_STATUS_NG			=	1
ITEM_STATUS_UNKNOWN		=	2
#ITEM_STATUS_NO_ITEM		=	3

#YZ移动方向
DIRECTION_UNKNOWN = 0
DIRECTION_LEFT = 1
DIRECTION_RIGHT =  2


INSTRUCTION_DEVICE_HANDSHAKE = "51 c0 00 11"
INSTRUCTION_DEVICE_SETWIDTH = "51 0x xx crc"
INSTRUCTION_DEVICE_RESET = "51 c0 01 12"
INSTRUCTION_DEVICE_SENDITEM = "51 c1 00 12"
INSTRUCTION_YZ_MOVE_MIDDLE_AND_SEND_ITEM = "51 c1 01 13"
INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM	= "51 c1 02 14"
INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM	= "51 c1 03 15"
INSTRUCTION_HCJ_RECV_ITEM_OK = "51 c2 04 17"
INSTRUCTION_HCJ_RECV_ITEM_NG = "51 c2 05 18"
INSTRUCTION_YZ_MOVE_MIDDLE_AND_RECV_ITEM = "51 c2 01 14"
INSTRUCTION_YZ_MOVE_LEFT_AND_RECV_ITEM = "51 c2 02 15"
INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM = "51 c2 03 16"
INSTRUCTION_DEVICE_GET_STATUS = "51 c4 00 15"

instruction_name_map = dict((eval(name), name) for name in ['INSTRUCTION_DEVICE_HANDSHAKE', 'INSTRUCTION_DEVICE_SETWIDTH', 'INSTRUCTION_DEVICE_RESET','INSTRUCTION_DEVICE_SENDITEM','INSTRUCTION_YZ_MOVE_MIDDLE_AND_SEND_ITEM','INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM','INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM','INSTRUCTION_HCJ_RECV_ITEM_OK','INSTRUCTION_HCJ_RECV_ITEM_NG','INSTRUCTION_YZ_MOVE_MIDDLE_AND_RECV_ITEM','INSTRUCTION_YZ_MOVE_LEFT_AND_RECV_ITEM','INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM','INSTRUCTION_DEVICE_GET_STATUS'])

def GetInstructionName(instruction):
	if(instruction_name_map.has_key(instruction)):
		return instruction_name_map[instruction]
	else:
		return instruction

EVENT_SHAKEHANDS_RES = "52 c0 00 12"
EVENT_AVAILABLE = "52 c1 f0 03"
EVENT_GETITEM_FINISHED = "52 c1 f1 04"
EVENT_SENDITEM_FINISHED = "52 c1 f2 05"
EVENT_HUANCUNJI_GETITEM_FINISHED = "52 c2 00 14"
EVENT_ASK_FOR_ITEM = "52 c3 08 1d"
EVENT_READYFOR_GETITEM = "52 c2 04 18"
EVENT_READYFOR_GETITEM_MIDDLE = "52 c2 01 15"
EVENT_READYFOR_GETITEM_LEFT = "52 c2 02 16"
EVENT_READYFOR_GETITEM_RIGHT = "52 c2 03 17"
EVENT_TESTING = "52 c1 f3 06"
EVENT_READYFOR_SENDITEM_OK = "52 c1 f4 07"
EVENT_READYFOR_SENDITEM_NG = "52 c1 f5 08"
EVENT_READYFOR_SENDITEM = "52 c1 f6 09"
EVENT_DEVICE_WARNING_1 = "52 c3 xx crc"
EVENT_DEVICE_WARNING_2 = "52 c3 00 15"
EVENT_DEVICE_WARNING_3 = "52 c3 01 16"
EVENT_DEVICE_WARNING_4 = "52 c3 02 17"
EVENT_HUANCUNJI_NOTREADY = "52 c3 03 18"


# status sent from device
RES_STATUS_AVAILABLE = "52 c4 01 17"			# 空闲 AVAILABLE
RES_STATUS_GETITEM_FINISHED = "52 c4 02 18"		# 接板完成（等待状态） WAITING
RES_STATUS_TESTING = "52 c4 03 19"				# 测试中 TESTING
RES_STATUS_BROKEN = "52 c4 04 1a"				# 故障报警（故障状态） BROKEN
RES_STATUS_READYFOR_SENDITEM = "52 c4 05 1b"	# 测试完成准备送板/准备好了送板（等待状态） WAITING
RES_STATUS_SENDITEM_FINISHED = "52 c4 06 1c"	# 送板完成（空闲状态） AVAILABLE
RES_STATUS_BUSY = "52 c4 07 1d"					# 忙碌 BUSY


event_name_map = dict((eval(name), name) for name in ['EVENT_SHAKEHANDS_RES','EVENT_AVAILABLE','EVENT_GETITEM_FINISHED','EVENT_SENDITEM_FINISHED', 'EVENT_HUANCUNJI_GETITEM_FINISHED', 'EVENT_ASK_FOR_ITEM','EVENT_READYFOR_GETITEM','EVENT_READYFOR_GETITEM_MIDDLE', 'EVENT_READYFOR_GETITEM_LEFT','EVENT_READYFOR_GETITEM_RIGHT','EVENT_TESTING','EVENT_READYFOR_SENDITEM_OK','EVENT_READYFOR_SENDITEM_NG','EVENT_READYFOR_SENDITEM','EVENT_DEVICE_WARNING_1','EVENT_DEVICE_WARNING_2','EVENT_DEVICE_WARNING_3','EVENT_DEVICE_WARNING_4','EVENT_HUANCUNJI_NOTREADY','RES_STATUS_BUSY',])


ERRCODE_STATUS_OF_ITEM_IN_PREVIOUS_DEVICE_IS_UNKNOWN		=	100
ERRCODE_DEVICE_IS_WITHOUT_SOCKET_WHILE_SENDING_INSTRUCTION	=	101


def RemoveBlankInMiddle(s):
	arr = string.split(s)
	result = "".join(x for x in arr)
	return result
	
def verifyPacket(buff):
	if(len(buff) != 4):
		hex_msg = ' '.join(x.encode('hex') for x in buff)
		writeWarning("INVALID PACKET [%s]" % hex_msg)
		return False
	return True
	#TODO 实现校验位检查	
def convert2Hex(msg):
	msg_list = string.split(msg, ' ')
	send_msg = ''
	for x in msg_list:
		send_msg += x.decode('hex')
	return send_msg