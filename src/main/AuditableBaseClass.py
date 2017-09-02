from Logger import Log

class AuditableBaseMetaClass(type):

	def __new__(meta, name, bases, dct):
		for attrname, attr in dct.items():
			if callable(attr):
				dct[attrname] = Log().__call__(attr)
		return super(AuditableBaseMetaClass, meta).__new__(meta, name, bases, dct)


class AuditableBaseClass(metaclass=AuditableBaseMetaClass):
	#__metaclass__=AuditableBaseMetaClass python2.7
	#TODO: add option to exclude a specific method/funtion from log to avoid performance issues.