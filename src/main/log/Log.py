import os
import logging
import errno
import logging.config
import datetime

LOGCONF = "../../config/logging/logging.conf"
LOGDIR = "../../tmp/logs/"

class Logger():
	
	if not os.path.exists(LOGDIR):
		try:
			os.makedirs(LOGDIR)
		except OSError as exc:
			if exc.errno == errno.EEXIST and os.path.isdir(LOGDIR):
				pass
			else:
				raise

	logging.config.fileConfig(os.path.abspath(LOGCONF), defaults={"logfilename":LOGDIR+"logging-"+str(datetime.datetime.today().date())+".conf"})    
	logger = logging.getLogger()
	
	@classmethod
	def getLogger(self):
		return self.logger
