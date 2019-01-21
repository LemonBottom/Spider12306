# Create time:2018-11-24 22:37
# Author:Chen

from twilio.rest import Client


class SendSMS:

	def __init__(self, to, msg):
		self.msg = msg
		self.to = "+86" + to
		self.account_sid = 'AC1d94e97982e1ed4a59542019aa521f47'
		self.auth_token = 'e9a6f08270059005dd144ad8bd2d2d08'
		self.send()

	def send(self):
		client = Client(self.account_sid, self.auth_token)
		client.messages.create(from_='+16267905464', body=self.msg, to=self.to)


