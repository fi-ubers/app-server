import json
import unittest
import os

from src.main.com import TokenGenerator


"""
Test class for TokenGenerator utility
"""
class TestTokenGenerator(unittest.TestCase):
	
	def test_decoded_gives_same_payload(self):
		payload = {"username" : "juan", "_id" : 1}
		token = TokenGenerator.generateToken(payload)
		valid, decoded = TokenGenerator.validateToken(token)
		assert(valid == True)
		assert(decoded == payload)

	def test_invalid_decode(self):
		token = "This is a fake token"
		valid, decoded = TokenGenerator.validateToken(token)
		assert('Invalid token' in decoded)
		assert(valid == False)

