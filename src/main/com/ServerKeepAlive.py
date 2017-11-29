import threading
import time
from src.main.com import Server

TIME = 120

class ServerKeepAlive(threading.Thread):
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.name = threadName
	
	def run(self):
		while True:
			time.sleep(TIME)
			Server.pingServer()

		
