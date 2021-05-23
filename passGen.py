import hashlib, random, sys, os, argparse, json
from getpass import getpass as gp
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ET

def updateVaultTable(vaultKeyPath):
	tmp = {}
	tmp = getVaultTable(vaultKeyPath)
	keyName = read('site alias? (i.e. "reddit")\n')
	tmp['passwords'][keyName] = read('enter pw:\n')
	vaultPath = getVaultPath()
	with open(vaultKeyPath,'rb') as mykey:
		key = mykey.read()
	f = Fernet(key)
	#TO-DO: error handling -- make sure file is locked
	with open(vaultPath,'w') as vault:
		json.dump(tmp,vault)
	encryptVaultTable(vaultKeyPath)

def getVaultTable(vaultKeyPath):
	vaultPath = getVaultPath()
	with open(vaultKeyPath,'rb') as mykey:
		key = mykey.read()
	f = Fernet(key)
	with open(vaultPath,'rb') as encryptedVault:
		encrypted = encryptedVault.read()
	decrypted = f.decrypt(encrypted)
	return json.loads(decrypted)

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
	if root[0].text == None:
		return os.path.dirname(os.path.abspath(__file__)) + '/.vault/vault.json'
	return root[0].text

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

def generateVaultKey(vaultKeyPath):
	print('generating vault.key....')
	key = Fernet.generate_key()
	with open(vaultKeyPath, 'wb') as mykey:
	    mykey.write(key)
	return vaultKeyPath

def createVault(vaultKeyPath):
	tmp = { "passwords" : {"tmp":"none"} }
	if os.path.exists('./.vault/vault.json'):
		print('!!!! WARNING: a vault already exists at ./vault/vault.json')
		option = read('Continue? This will overwrite vault existing at ./vault/vault.json [y/n]: ')
		if option.lower() == 'y':
			os.remove(vaultKeyPath)
			os.remove('./.vault/vault.json')
		elif option.lower() == 'n':
			print('Aborting vault creation....\n')
			return vaultKeyPath
		else:
			print('No option selected')
			return vaultKeyPath
	if not os.path.exists('./.vault'):
		os.mkdir('./.vault')
	with open('./.vault/vault.json','w+') as f:
		json.dump(tmp,f)
	f.close()
	print('vault created at ./.vault/\n')
	newVaultKeyPath = './.hide/vault.key'
	generateVaultKey(newVaultKeyPath)
	return newVaultKeyPath

def hashInputPlusSalt(userInput,saltVal):
	return hashlib.sha256((userInput + str(saltVal)).encode()).hexdigest()

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

def getPWseed():
	return gp('Enter password seed: ')

def generateNewPW():
	tmp = getPWseed()
	index = int(round(random.randrange(0,999)))
	i = 0
	literalHashTable = []
	while i < 1000:
		saltObj = salt()
		literalHashTable.append(hashInputPlusSalt(tmp,saltObj.getSalt()))
		i += 1
	print('new password: ',literalHashTable[index])

def read(prompt):
	if sys.version_info[0] == 2:
		return raw_input(prompt)
	else:
		return input(prompt)

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
		cmd = read('\n==passGen==\n\nOptions:\ngenPass = generate 64 char password\nvaultInit = create new vault\ngetVault = read vault values\nupdateVault = add vault value\nquit = close session\n\nInput command: ')
		if cmd == 'genPass':
			generateNewPW()
		elif cmd == 'vaultInit':
			vaultKeyPath[0] = createVault(vaultKeyPath[0])
			encryptVaultTable(vaultKeyPath[0])
			print(vaultKeyPath[0])
		elif cmd == 'getVault':	
			if not os.path.exists(vaultKeyPath[0]):
				print('ERROR: No vault key found at ', vaultKeyPath[0])
			else:
				try:
					print(json.dumps(getVaultTable(vaultKeyPath[0]),sort_keys=True,indent=4))
				except:
					print(getVaultTable(vaultKeyPath[0]))
		elif cmd == 'updateVault':
			if not os.path.exists(vaultKeyPath[0]):
				print('ERROR: No vault key found at ', vaultKeyPath[0])
			else:
				updateVaultTable(vaultKeyPath[0])		
		elif cmd == 'quit':
			break
		else:
			print('no option selected')

if __name__ == '__main__':
	main()