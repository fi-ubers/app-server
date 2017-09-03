#from ..main.Logger import Log
import inspect
from ..main.Logger import Log


class AuditableBaseClass(object):
	#__metaclass__=AuditableBaseMetaClass python2.7
	#TODO: add option to exclude a specific method/funtion from log to avoid performance issues.
	def __init__(self):
		self.exclude = [ "__init__"]	
		#self.logger = Log()

	def __getattribute__(self, name):
		attr = super(AuditableBaseClass, self).__getattribute__(name)
		if callable(attr) and (attr.__name__ not in self.exclude):
			attr =  Log().__call__(attr)
		return attr
