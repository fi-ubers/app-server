import logging
import logging.config
from os import path
from functools import wraps

CONFIG_FILE = "logging.conf"
LOG_NAME = "logger1"
#LOGFNAME = "logging.log"

class Log(object):
	def __init__(self, msg = "", log = LOG_NAME, config = CONFIG_FILE):
		#TODO: this should only be called once
		#TODO: dinamically specify logfilename to be inserted in config file
		logging.config.fileConfig(path.join(path.dirname(path.abspath(__file__)), config), disable_existing_loggers=False) 
		#
		self.logger = logging.getLogger(LOG_NAME)
		self.message = msg
		
	def __call__(self, func):
		#Allows the log to be used as a decorator.
		def wrapper(*args, **kwargs):            
			return func(*args, **kwargs)
		print "HOLAAAAAAAa"
		self.logger.debug("Function {}. MSG: {}".format(str(func.__name__), str(self.message)))
		return wrapper

