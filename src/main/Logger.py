import sys
import logging
import logging.config
import os
from os import path
from functools import wraps
import datetime

CONFIG_FILE = "../../config/logging.conf"
LOG_NAME = "logger"
LOG_PATH = "tmp/log/"

class Log(object):
	def __init__(self, msg = "", log = LOG_NAME, config = CONFIG_FILE):
		#TODO: this should only be called once
		#TODO: dinamically specify logfilename to be inserted in config file
		if not os.path.exists(LOG_PATH):
			os.makedirs(LOG_PATH)
		logging.config.fileConfig(path.join(path.dirname(path.abspath(__file__)), config), defaults={"logfilename": LOG_PATH + "log-"+str(datetime.date.today())+".log"}, disable_existing_loggers=False) 
		#
		self.logger = logging.getLogger(LOG_NAME)
		self.message = ("" if(msg != "") else "MSG: ") + msg

	def __call__(self, func):
		#Allows the log to be used as a decorator.
		@wraps(func)
		def wrapper(*args, **kwargs):            
			try:		
				self.logger.debug("Function/Method {}. {}".format(str(func.__name__), str(self.message)))
				return func(*args, **kwargs)
			except:
				e = sys.exc_info()[0]
				errorMsg = "An error has ocurred: {}".format(str(e))
				self.logger.exception(errorMsg)
				raise
		return  wrapper 
