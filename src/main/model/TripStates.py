"""
These are the states a trip can be in.
Refer to this module when setting or comparing trip states.
"""

TRIP_PROPOSED = "proposed"
TRIP_ACCEPTED = "accepted"
TRIP_CONFIRMED = "confirmed"
TRIP_STARTED_PASSENGER = "started_passenger"
TRIP_STARTED_DRIVER = "started_driver"
TRIP_STARTED = "started"

TRIP_START_VALID = [TRIP_CONFIRMED, TRIP_STARTED_PASSENGER, TRIP_STARTED_DRIVER]


ACTION_CANCEL = "cancel"
ACTION_DRIVER_ACCEPT = "accept"
ACTION_PASSENGER_CONFIRM = "confirm"
ACTION_PASSENGER_REJECT = "reject"
ACTION_START = "start"
ACTION_FINISH = "finish"
