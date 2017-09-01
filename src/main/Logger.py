import logging
import logging.config
from os import path
from functools import wraps

CONFIG_FILE = "logging.conf"
LOG_NAME = "logger1"

class Log(object):
	def __init__(self, msg = "", log = LOG_NAME, logfname = CONFIG_FILE):
		#TODO: esto deberia llamarse una sola vez
		logging.config.fileConfig(path.join(path.dirname(path.abspath(__file__)), logfname), disable_existing_loggers=False) 
		#
		self.logger = logging.getLogger(LOG_NAME)
		self.message = msg

	def __call__(self, func):
		def wrapper(*args, **kwargs):            
			return func(*args, **kwargs)
		self.logger.debug("Function {}. MSG: {}".format(str(func.__name__), str(self.message)))
		return wrapper
	#def log(msg=""):
	#	def log_decorator(func):
	#		@wraps(func)
	#		def wrapper(*args, **kwargs):            
	#			return func(*args, **kwargs)
	#		logger.debug("Function {}. MSG: {}".format(str(func.__name__), str(msg)))
	#		return wrapper
	#	return log_decorator 

