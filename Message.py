# -*- coding: utf-8 -*-
#!/usr/bin/env python 

import string 

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 10002
CLIENT_HOST = '127.0.0.1'
CLIENT_PORT = 10003

#最低8bit标识设备的状态
S_IDLE							=	0x0000	# 空闲
S_PREPARING_TO_RECV				=	0x0001	# 移栽机在移动中
S_HALF_READY_TO_RECV_ITEM		=	0x0002	# 移栽机已经到达接板位置, 但是需要再次确认其准备好了
S_READY_TO_RECV_ITEM 			=	0x0003 	# 准备好接板
S_RECVING						=	0x0004	# 接板中
S_WITH_ITEM						=	0x0005	# 设备上有板子    
S_TESTING						=	0x0006	# 测试中      
S_READY_TO_SEND_ITEM			=	0x0007	# 准备好送板
S_SENDING						=	0x0008	# 送板中    
S_BROKEN						=	0x0009	# 故障状态    
S_RESETTING						=	0x000A	# 重启中    
S_UNKNOWN						=	0xFFFF	# 未知状态

#所携带的板子的状态
ITEM_STATUS_OK			=	0
ITEM_STATUS_NG			=	1
ITEM_STATUS_UNKNOWN		=	2
#ITEM_STATUS_NO_ITEM		=	3


INSTRUCTION_DEVICE_HANDSHAKE = "51 c0 00 11"
INSTRUCTION_DEVICE_SETWIDTH = "51 0x xx crc"
INSTRUCTION_DEVICE_RESET = "51 c0 01 12"
INSTRUCTION_DEVICE_SENDITEM = "51 c1 00 12"
INSTRUCTION_YZ_MOVE_MIDDLE_AND_SEND_ITEM = "51 c1 01 13"
INSTRUCTION_YZ_MOVE_LEFT_AND_SEND_ITEM	=	"51 c1 02 14"
INSTRUCTION_YZ_MOVE_RIGHT_AND_SEND_ITEM	=	"51 c1 03 15"
INSTRUCTION_HCJ_RECV_ITEM_OK = "51 c2 00 13"
INSTRUCTION_HCJ_RECV_ITEM_NG = "51 c2 10 23"
INSTRUCTION_YZ_MOVE_MIDDLE_AND_RECV_ITEM = "51 c2 01 14"
INSTRUCTION_YZ_MOVE_LEFT_AND_RECV_ITEM = "51 c2 02 15"
INSTRUCTION_YZ_MOVE_RIGHT_AND_RECV_ITEM = "51 c2 03 16"
INSTRUCTION_DEVICE_GET_STATUS = "51 c4 00 15"


EVENT_SHAKEHANDS_RES = "52 c0 00 12"
EVENT_SETWIDTH_RES = "52 0x xx crc"
EVENT_RESET_STATUS_RES = "52 0x xx crc"
EVENT_AVAILABLE = "52 c1 f0 03"
EVENT_GETITEM_FINISHED = "52 c1 f1 04"
EVENT_SENDITEM_FINISHED = "52 c1 f2 05"
EVENT_HUANCUNJI_GETITEM_FINISHED = "52 c2 00 14"
EVENT_READYFOR_GETITEM_OK = "52 c3 04 19"
EVENT_READYFOR_GETITEM_NG = "52 c3 05 1a"
EVENT_ASK_FOR_ITEM = "52 c3 08 1d"
EVENT_HUANCUNJI_BUSY = "52 c3 06 1b"
EVENT_HUANCUNJI_GETITEM_ERROR = "52 c3 07 1c"
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


ERRCODE_STATUS_OF_ITEM_IN_PREVIOUS_DEVICE_IS_UNKNOWN		=	100
ERRCODE_DEVICE_IS_WITHOUT_SOCKET_WHILE_SENDING_INSTRUCTION	=	101


def RemoveBlankInMiddle(s):
	arr = string.split(s)
	result = "".join(x for x in arr)
	return result
	
def verifyPacket(buff):
	if(len(buff) != 4):
		hex_msg = ' '.join(x.encode('hex') for x in buff)
		print "Invalid Packet [%s]" % hex_msg
		return False
	return True
	#TODO 实现校验位检查	
	