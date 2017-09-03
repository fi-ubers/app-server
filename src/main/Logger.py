import sys
import logging
import logging.config
from os import path
from functools import wraps

CONFIG_FILE = "logging.conf"
LOG_NAME = "logger"

class Log(object):
	def __init__(self, msg = "", log = LOG_NAME, config = CONFIG_FILE):
		#TODO: this should only be called once
		#TODO: dinamically specify logfilename to be inserted in config file
		logging.config.fileConfig(path.join(path.dirname(path.abspath(__file__)), CONFIG_FILE), disable_existing_loggers=False) 
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