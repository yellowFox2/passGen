import hashlib, random, sys, os, argparse, json
from salt import salt
from vaultTable import vaultTable
from getpass import getpass as gp

def hashInputPlusSalt(userInput,saltVal):
	return hashlib.sha256((userInput + str(saltVal)).encode()).hexdigest()

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
    vault = vaultTable(getArgs())
    while(1):
        cmd = read('\n==passGen==\n\nOptions:\ngenPass = generate 64 char password\nvaultInit = create new vault\ngetVault = read vault values\nupdateVault = add vault value\nquit = close session\n\nInput command: ')
        if cmd == 'genPass':
            generateNewPW()
        elif cmd == 'vaultInit':
            if os.path.exists('./.vault/vault.json'):
                print('!!!! WARNING: a vault already exists at ./vault/vault.json')
                option = read('Continue? This will overwrite vault existing at ./vault/vault.json [y/n]: ')
                if option.lower() == 'y':
                    os.remove(vault.getVaultKeyPath())
                    os.remove('./.vault/vault.json')
                    vault.createVaultTable()
                elif option.lower() == 'n':
                    print('Aborting vault creation....\n')
                else:
                    print('No option selected')
            else:
                vault.createVaultTable()
        elif cmd == 'getVault':	
            if not os.path.exists(vault.getVaultKeyPath()):
                print('ERROR: No vault key found at ', vault.getVaultKeyPath())
            else:
                try:
                    print(json.dumps(vault.getVaultTable(),sort_keys=True,indent=4))
                except:
                    print(vault.getVaultTable())
        elif cmd == 'updateVault':
            if not os.path.exists(vault.getVaultKeyPath()):
                print('ERROR: No vault key found at ', vault.getVaultKeyPath())
            else:
                siteAlias = read('site alias? (i.e. "reddit")\n')
                pw = read('enter pw:\n')
                vault.updateVaultTable(siteAlias,pw)		
        elif cmd == 'quit':
            break
        else:
            print('no option selected')

if __name__ == '__main__':
	main()