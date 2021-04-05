import hashlib, time, random, sys, os, argparse, json
from threading import Thread, Lock
from getpass import getpass as gp
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ET

#TODO: logging/error handling

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
	return vaultKeyPath

def storeVaultKey(): #store private key locally (somewhere safe)
	pass

def getVaultPath():
	args = getArgs()
	if args.config:
		if os.path.exists(args.config):
			xml = ET.parse(args.config)
		else:
			xmlPath = os.path.dirname(os.path.abspath(__file__)) + '/config/config.xml'
			xml = ET.parse(xmlPath)
	else:
		xmlPath = os.path.dirname(os.path.abspath(__file__)) + '/config/config.xml'
		xml = ET.parse(xmlPath)
	root = xml.getroot()
	return root[1].text

def encryptVaultTable(vaultKeyPath):
	with open(vaultKeyPath,'rb') as mykey:
		key = mykey.read()
	f = Fernet(key)
	vaultPath = getVaultPath()
	with open(vaultPath,'rb') as unencryptedVault:
		unencrypted = unencryptedVault.read()
	encrypted = f.encrypt(unencrypted)
	with open(vaultPath,'wb') as encryptedVault:
		encryptedVault.write(encrypted)

def getVaultTable(vaultKeyPath): #decrypt vault table first
	vaultPath = getVaultPath()
	with open(vaultKeyPath,'rb') as mykey:
		key = mykey.read()
	f = Fernet(key)
	with open(vaultPath,'rb') as encryptedVault:
		encrypted = encryptedVault.read()
	decrypted = f.decrypt(encrypted)
	return json.loads(decrypted)

def updateVaultTable(vaultKeyPath):
	tmp = {}
	tmp = getVaultTable(vaultKeyPath)
	keyName = read('site alias? (i.e. "reddit")\n')
	#tmp['passwords'][keyName] = getUserPW()
	tmp['passwords'][keyName] = read('enter pw:\n')
	setVaultTable(tmp,vaultKeyPath)

def setVaultTable(tmpTable,vaultKeyPath): #save dict to json and encrypt with key
	vaultPath = getVaultPath()
	with open(vaultKeyPath,'rb') as mykey:
		key = mykey.read()
	f = Fernet(key)
	#TO-DO: error handling -- make sure file is locked
	with open(vaultPath,'w') as vault:
		json.dump(tmpTable,vault)
	encryptVaultTable(vaultKeyPath)

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

def createVault(vaultKeyPath):
	tmp = { "passwords" : {"tmp":"none"} }
	with open('./.vault/new-vault.json','w+') as f:
		json.dump(tmp,f)
	f.close()
	print('vault created at ./.vault/\n')
	newVaultKeyPath = './.hide/new-vault.key'
	generateVaultKey(newVaultKeyPath)
	return newVaultKeyPath

def getArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-k','--key')
	parser.add_argument('-c','--config')
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
	while(1):
		cmd = read('run cmd\n')
		if cmd == 'genPass':
			generateNewPW()
		elif cmd == 'vaultInit':
			vaultKeyPath[0] = createVault(vaultKeyPath[0])
			print(vaultKeyPath[0])
		elif cmd == 'getVault':		
			try:
				print(json.dumps(getVaultTable(vaultKeyPath[0]),sort_keys=True,indent=4))
			except:
				print(getVaultTable(vaultKeyPath[0]))
		elif cmd == 'genVaultKey':
			print(vaultKeyPath[0])
			generateVaultKey(vaultKeyPath[0])
		elif cmd == 'updateVault':
			updateVaultTable(vaultKeyPath[0])
		elif cmd == 'encryptVault':
			encryptVaultTable(vaultKeyPath[0])			
		elif cmd == 'updateKeyPath':
			print(vaultKeyPath[0])
			vaultKeyPath[0] = updateKeyPath()
		elif cmd == 'quit':
			break
		else:
			print('no option selected')

if __name__ == '__main__':
	main()