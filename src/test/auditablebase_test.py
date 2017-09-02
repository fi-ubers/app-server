from ..main.AuditableBaseClass import AuditableBaseClass
import unittest

class AuditableBaseClassTest:

	def testAuditableBaseClassMethodIsLogged():
		abc = AuditableBaseClass()
		#abc.someMethod = MagicMock(return_value="hello")
		assert os.path.exists("testing.log")


