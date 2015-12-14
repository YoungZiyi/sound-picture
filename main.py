# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import Qt
from PyQt4 import *
from spiderman import *
import sys
from threading import *
import socket
import time
from bxtcommon import *

from Message import *
from Device import *

class ExampleApp(QtGui.QMainWindow, Ui_MainWindow):
	def __init__(self, parent=None):
		super(ExampleApp, self).__init__(parent)
		self.setupUi(self)

	def send_msg_to_server(self):
		objectName = str(self.sender().objectName())
		'''
		if objectName in ['jiebotai0_Ready', 'ICT_Ready', 'huancunji_Ready', 'jiebotai1_Ready', 'NGshouban_Ready', 'OKshouban_Ready']:
			# 空闲（准备好接板）
			order = '52c40117'
		elif objectName in ['jiebotai0_GetItemFinish', 'ICT_GetItemFinish', 'huancunji_GetItemFinish', 'jiebotai1_GetItemFinish']:
			# 接板完成
			order = '52c40218'
		elif objectName in ['ICT_Testing']:
			# 测试中
			order = '52c40319'
		elif objectName in ['ICT_Warning', 'huancunji_Warning', 'OKshouban_Warning', 'NGshouban_Warning']:
			# 故障报警
			order = '52c4041a'
		elif objectName in ['jiebotai0_ReadyToSendItem', 'ICT_ReadyToSendItem', 'huancunji_ReadyToSendItem', 'jiebotai1_ReadyToSendItem']:
			# （测试完成）准备好了送板
			order = '52c4051b'
		elif objectName in ['jiebotai0_SendItemFinish', 'ICT_SendItemFinish', 'huancunji_SendItemFinish', 'jiebotai1_SendItemFinish', 'OKshouban_SendItemFinish', 'NGshouban_SendItemFinish']:
			# 接板完成
			order = '52c4061c'
		elif objectName in ['jiebotai0_Busy', 'ICT_Busy', 'huancunji_Busy', 'jiebotai1_Busy', 'OKshouban_Busy', 'NGshouban_Busy']:
			# 忙碌
			order = '52c4071d'

		elif objectName == 'all_ShakeHands':
			# 握手（反馈）
			order = '52c00012'
		elif objectName == 'SetWidthBack':
			# 调宽反馈
			order = '520xxxcrc'
		else:
			order = str(objectName)
		sendToPeer(SERVER_HOST, SERVER_PORT, order)
		'''
		device = objectName.split('_', 1)[0]
		msg = objectName.split('_', 1)[1]
		print objectName

def thread_recv_msg_from_server(qlabel):
	print "communication thread is up"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((CLIENT_HOST, CLIENT_PORT))
	s.listen(1)
	print 'Waiting...'

	while 1:
		try:
			conn, addr = s.accept()
			print 'connected by:', addr
			data = conn.recv(2048)
			print "recv:\t", data
			conn.close();
			qlabel.setText(data)
		except Exception, e:
			print "thread_recv_msg_from_server"
			print e

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.show()

    t = Thread(target=thread_recv_msg_from_server, args = (form.instruction,))
    t.daemon = True
    t.start()

    app.exec_()