# -*- coding: utf-8 -*-
#!/usr/bin/env python 

debugging = True

flag_exit = False
def signal_handler(signum, frame):
	global flag_exit
	flag_exit = True
	print "receive a signal %d, flag_exit = %d"%(signum, flag_exit)
