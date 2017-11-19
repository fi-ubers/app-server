from pyfcm import FCMNotification

API_KEY = "AAAAvAIsBoY:APA91bHa2aB5G6j1to5j7xSaS6NL83RYWK79_Vl0Zss5xCGhRp3QAFuEEsbpX-RfTXK8ISQNZRy6ajsSm4hSQiSiX18riN2qMbIXme8mLUpIReYQVXSNHxUEr0B_CI9fyYNaaTapJSLq"
push_service = FCMNotification(api_key=API_KEY)

class NotificationManager(object):
	
	def sendNotificationToTopic(self, topicName, messageText):
		# Send a message (messageText) to devices subscribed to a topic named topicName.
		result = push_service.notify_topic_subscribers(topic_name=topicName, message_body=messageText)
 		return result

# Conditional topic messaging
 #topic_condition = "'TopicA' in topics && ('TopicB' in topics || 'TopicC' in topics)"
 #result = push_service.notify_topic_subscribers(message_body=message, condition=topic_condition)
# FCM first evaluates any conditions in parentheses, and then evaluates the expression from left to right.
# In the above expression, a user subscribed to any single topic does not receive the message. Likewise,
# a user who does not subscribe to TopicA does not receive the message. These combinations do receive it:
# TopicA and TopicB
# TopicA and TopicC

