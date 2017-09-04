import sys
import os.path
import pytest
import datetime
from ..main.Logger import Log

LOGFNAME = "../../logs/log-"+str(datetime.date.today())+".log"
CONFIG = "../../config/loggingTest.conf"
LOGNAME = "testLogger"
TEST_MSG = "This is test msg"

class TestLogger(object):

	def testLogCallsFunction(self):
		@Log(TEST_MSG + " #1", LOGNAME + "1", CONFIG)
		def test():
			return TEST_MSG
		testResult = test()
		assert  testResult == TEST_MSG

	def testLogCreatesLogFile(self):
		#TODO: change logging file to test file so as not to
		#remove actual logging file while testing.		
		@Log(TEST_MSG + " #2", LOGNAME + "2", CONFIG)
		def test():
			return TEST_MSG
		testResult = test()
		assert os.path.exists(LOGFNAME)
		
