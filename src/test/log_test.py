import sys
import os.path
from ..main.Logger import Log

TEST_MSG = "LOG TEST #1"

@Log("LOGGER MSG")
def test():
	return TEST_MSG


class TestLogger(object):

	def testLogCallsFunction(self):
		assert test() == TEST_MSG

	def testLogCreatesLogFile(self):
		test()
		assert os.path.exists("testing.log")


