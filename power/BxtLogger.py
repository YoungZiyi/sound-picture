import logging
import time

Format = "%(asctime)s %(levelname)s  %(message)s"
DateFmt = "%Y-%m-%d %I:%M:%S"
FileName = "log/%s.log" % time.strftime("%Y-%m-%d", time.gmtime())
FileMode = "a"

logging.basicConfig(format = Format, datefmt = DateFmt, filename = FileName, filemode = FileMode, level = logging.DEBUG)

def writeDebug(msg):
	logging.debug(msg)

def writeInfo(msg):
	logging.info(msg)

def writeWarning(msg):
	logging.warning(msg)

def writeError(msg):
	logging.error(msg)

def writeCritical(msg):
	logging.critical(msg)