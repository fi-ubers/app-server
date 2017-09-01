import logging
import logging.config
from os import path
from functools import wraps

CONFIG_FILE = "logging.conf"

logging.config.fileConfig(path.join(path.dirname(path.abspath(__file__)), CONFIG_FILE), disable_existing_loggers=False)
logger = logging.getLogger("logger1")
		
#def logErr(f):
#	@wraps(f)
#	def wrapped(inst, *args, **kwargs):            
#       return f(inst, *args, **kwargs)
#    return wrapped

def log(msg=""):
	def log_decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):            
			return func(*args, **kwargs)
		logger.debug("Function {}. MSG: {}".format(str(func.__name__), str(msg)))
		return wrapper
	return log_decorator 

