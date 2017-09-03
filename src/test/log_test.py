import sys
import os.path
import pytest
from ..main.Logger import Log

TEST_MSG = "LOG TEST #1"
LOGFNAME = "logging.log"

@Log(TEST_MSG)
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
		