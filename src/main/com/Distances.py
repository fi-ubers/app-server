import logging as logger
from geopy.distance import great_circle


"""
Given who coordinates src and dst computes the great_circle
distance (asumes Earth is a perfect sphere). Input coordinates
should have the following dictionary format:
	src = { lat : <latitude>, lng : <longitude> }
Return value is the distance in meters.
"""
def computeDistance(src, dst):
	x = pointFromCoords(src)
	y = pointFromCoords(dst)
	print(x)
	print(y)
	return great_circle(x, y).m


"""
Converts a { lat: <lat>, lng: <lng> } dictionary (a coordinate)
into a tuple (lat, lng)
"""
def pointFromCoords(coords):
	return (float(coords["lat"]), float(coords["lng"]))



"""
Helper class to compare distances with respect to a fixed point.
When created it can be initialized with the "center point".
Then it's function cmp can be used to sort.
"""
class EgocentricDistance(object):
	
	def __init__(self, origin):
		self.origin = origin 

	def cmp(self, A, B):
		distA = computeDistance(origin, A)
		distB = computeDistance(origin, B)
		if distA > distB:
			return 1
		elif distA == distB:
			return 0
		return -1
