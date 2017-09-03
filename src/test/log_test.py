import sys
import os.path
from ..main.Logger import Log

TEST_MSG = "LOG TEST #1"
LOGFNAME = "logging.log"
#CONFIG_FILE = "../test/loggingTest.conf"

@Log(TEST_MSG)#, "logger1", CONFIG_FILE)
def test():
	return TEST_MSG

class TestLogger(object):

	def testLogCallsFunction(self):
		testResult = test()
		assert  testResult == TEST_MSG

	def testLogCreatesLogFile(self):
		#TODO: change logging file to test file so as not to
		#remove actual logging file while testing.		
		assert os.path.exists(LOGFNAME)


