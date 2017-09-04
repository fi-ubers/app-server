import os.path
import datetime
from src.main.log.AuditableBaseClass import AuditableBaseClass
from src.main.log.Logger import Log

LOGFNAME = "tmp/logs/log-"+str(datetime.date.today())+".log"

class _TestClass(AuditableBaseClass):
		def saySomething(self, string):
			return "Hello:" + string

class TestAuditableBaseClass(object):

	def testAuditableBaseClassMethodIsLogged(self):
		abc = _TestClass()
		abc.saySomething("abc")
		assert os.path.exists(LOGFNAME)
