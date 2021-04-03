import hashlib, time, random, sys, os, argparse, json
from threading import Thread, Lock
from getpass import getpass as gp
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ET

#TODO: password vault
#Will contain dictionary of urls and passwords
#Encrypt dictionary as string -- need to pick encoding for string


def read(prompt):
	if sys.version_info[0] == 2:
		return raw_input(prompt)
	else:
		return input(prompt)

def generateVaultKey(vaultKeyPath): #only once. used to access vault table
	print('generating vault.key....')
	key = Fernet.generate_key()
	with open(vaultKeyPath, 'wb') as mykey: #have user input location of key (secure input string)
	    mykey.write(key)

def storeVaultKey(): #store private key locally (somewhere safe)
	pass



def getVaultTable(vaultKeyPath): #decrypt vault table first
	xmlPath = os.path.dirname(os.path.abspath(__file__)) + '/config/config.xml'
	xml = ET.parse(xmlPath)
	root = xml.getroot()
	return json.load(open(root[1].text))

def setVaultTable(tmpTable,vaultKeyPath): #save dict to json and encrypt with key
	xmlPath = os.path.dirname(os.path.abspath(__file__)) + '/config/config.xml'
	xml = ET.parse(xmlPath)
	root = xml.getroot()
	vaultPath = root[1].text
	with open(vaultKeyPath,'rb') as mykey:
		key = mykey.read()
	f = Fernet(key)
	with open(vaultPath,'wb') as vault:
		json.dump(tmpTable,vault)
	with open(vaultPath,'rb') as unencryptedVault:
		unencrypted = unencryptedVault.read()
	encrypted = f.encrypt(unencrypted)
	with open(vaultPath,'wb') as encryptedVault:
		encryptedVault.write(encrypted)

class vaultTable:
	def __init__(self,config):
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
		preHash = str(int(round(randomNumSized)))
		self.salt = hashlib.sha1(preHash.encode()).hexdigest()

	def getSalt(self):
		return self.salt

	def __init__(self):
		self.setIntSize()
		self.setSalt()

def hashInputPlusSalt(userInput,saltVal):
	return hashlib.sha256((userInput + str(saltVal)).encode()).hexdigest()

def getUserPW():
	return gp('Enter pw\n')

def generateNewPW():
	tmp = getUserPW()
	index = int(round(random.randrange(0,999)))
	i = 0
	literalHashTable = []
	while i < 1000:
		saltObj = salt()
		literalHashTable.append(hashInputPlusSalt(tmp,saltObj.getSalt()))
		i += 1
	print('new password: ',literalHashTable[index])

def updateKeyPath():
	tmp = read('enter new key path:\n')
	if tmp == 'quit':
		return
	elif os.path.exists(tmp):
		return tmp
	else:
		print('path does not exist')
		return updateKeyPath()

def getArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-k','--key')
	return parser.parse_args()

def main():
	args = getArgs()
	vaultKeyPath = []
	if args.key == None:
		vaultKeyPath.append('./.hide/vault.key')		
	elif os.path.exists(args.key):
		vaultKeyPath.append(args.key)
	else:
		print('invalid path')
		vaultKeyPath.append('./.hide/vault.key')	
	print('Using key path: %s' % vaultKeyPath[0])
	print(getVaultTable(vaultKeyPath[0]))
	while(1):
		cmd = read('run cmd\n')
		if cmd == 'genPass':
			generateNewPW()
			#TO-DO: add option to update record in vault with new password
			#TESTING:
			test1 = { "testname" : "akshat", "test2name" : "manjeet", "test3name" : "nikhil" }
			setVaultTable(json.dumps(test1),vaultKeyPath[0])
		elif cmd == 'genVaultKey':
			generateVaultKey(vaultKeyPath[0])
		elif cmd == 'updateKeyPath':
			print(vaultKeyPath[0])
			vaultKeyPath[0] = updateKeyPath()
		elif cmd == 'quit':
			break
		else:
			print('no option selected')

if __name__ == '__main__':
	main()
