import os.path
import datetime
from ..main.AuditableBaseClass import AuditableBaseClass
from ..main.Logger import Log

LOGFNAME = "../../logs/log-"+str(datetime.date.today())+".log"

class _TestClass(AuditableBaseClass):
		def saySomething(self, string):
			return "Hello:" + string

class TestAuditableBaseClass(object):

	def testAuditableBaseClassMethodIsLogged(self):
		abc = _TestClass()
		abc.saySomething("abc")
		assert os.path.exists(LOGFNAME)
