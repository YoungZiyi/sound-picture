import logging
import time

Format = "%(asctime)s: %(message)s"
DateFmt = "%Y_%m_%d %H:%I:%S"
FileName = "Log/%s.txt" % time.strftime("%Y_%m_%d", time.gmtime())
FileMode = "a"

logging.basicConfig(format = Format, datefmt = DateFmt, filename = FileName, filemode = FileMode, level = logging.DEBUG)
'''
logging.debug("debug")
logging.info("info")
logging.warning("warning")
logging.error("error")
logging.critical("critical")
'''

def writeInfo(msg):
	logging.info(msg)

def writeWarning(msg):
	logging.warning(msg)

def writeError(msg):
	logging.error(msg)

def writeCritical(msg):
	logging.critical(msg)