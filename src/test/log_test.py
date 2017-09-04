import sys
import os.path
import pytest
import datetime
from src.main.log.Logger import Log

LOGFNAME = "tmp/logs/log-"+str(datetime.date.today())+".log"
CONFIG = "config/loggingTest.conf"
LOGNAME = "testLogger"
TEST_MSG = "This is test msg"

@Log(TEST_MSG + " #1", CONFIG)
def test():
	return TEST_MSG


class TestLogger(object):

	def testLogCallsFunction(self):
		assert  test() == TEST_MSG

	def testLogCreatesLogFile(self):
		#TODO: change logging file to test file so as not to
		#remove actual logging file while testing.		
		test()
		assert os.path.exists(LOGFNAME)
	
	
