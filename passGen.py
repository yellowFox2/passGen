import hashlib, time, random
from threading import Thread, Lock
from getpass import getpass as gp




#TODO: password vault
#Will contain dictionary of urls and passwords
def generateVaultKey(): #only once. used to access vault table (private key)
	pass

def storeVaultKey(): #store private key locally (somewhere safe)
	pass

def getVaultTable(): #decrypt vault key then retrieve (public key)
	pass

def setVaultTable():
	pass

 


class salt:
	def setIntSize(self):
		while(1):
			self.intSize = int(round(random.random() * 10,1))
			if self.intSize != 0:
				break

	def getIntSize(self):
		return self.intSize

	def setSalt(self):
		randomNum = random.random()
		randomNumSized = randomNum * (10 ** self.getIntSize())
		preHash = str(round(randomNumSized))
		print('salt prehash: ',preHash)
		self.salt = hashlib.sha1(preHash.encode()).hexdigest()
		print('salt: ', self.salt)

	def getSalt(self):
		return self.salt

	def __init__(self):
		self.setIntSize()
		self.setSalt()

def hashInputPlusSalt(userInput,saltVal):
	inPlusSalt = userInput + str(saltVal)
	print(inPlusSalt)
	return hashlib.sha256(inPlusSalt.encode()).hexdigest()

def getUserInput():
	return gp('Enter pw\n')

def generateNewPW(tmp):
	index = int(round(random.randrange(0,999)))
	print('literalHashTable index: ',index)
	i = 0
	literalHashTable = []
	while i < 1000:
		saltObj = salt()
		literalHashTable.append(hashInputPlusSalt(tmp,saltObj.getSalt()))
		i += 1
	print('new password: ',literalHashTable[index])

#test
generateNewPW(getUserInput())