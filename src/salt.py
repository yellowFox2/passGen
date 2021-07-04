import hashlib, random

class salt:

	def setIntSize(self):
		while 1:
			self.intSize = int(round(random.random() * 10,1))
			if self.intSize != 0:
				break

	def getIntSize(self):
		return self.intSize

	def setSalt(self):
		randomNum = random.random()
		randomNumSized = randomNum * (10 ** self.getIntSize())
		preHash = str(int(round(randomNumSized)))
		self.salt = hashlib.sha1(preHash.encode()).hexdigest()

	def getSalt(self):
		return self.salt

	def __init__(self):
		self.setIntSize()
		self.setSalt()
        