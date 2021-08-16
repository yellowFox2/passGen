import hashlib, random, sys, argparse, os, json, time, platform, gc
import xml.etree.ElementTree as ET
from src.salt import salt
from src.vaultTable import vaultTable as VT
from src.vaultKey import vaultKey as VK
from src.config import config
from src.bash import bash

try:
    import ipfshttpclient as IPFS
except ImportError:
    IPFS = None

OS = 'unix' if sys.platform == 'linux' else 'windows'
PYTHON_VERSION = '2' if sys.version_info[0] == 2 else '3'
SCRIPT_PATH = [os.path.dirname(os.path.abspath(__file__)).replace('\\','/'), 'str']
DEFAULT_HIDE_PATH = ['/.hide/vault.key', 'str']
DEFAULT_VAULT_PATH = ['/.vault/vault.json', 'str']
DEFAULT_CONFIG_PATH = ['/config/config.xml', 'str']
VAULT_PATH = ['vaultPath','str', SCRIPT_PATH[0] + DEFAULT_VAULT_PATH[0]]
HASH_LIST_LEN = ['hashListSize', 'int', 1500]
SPEC_CHAR_CHANCE = ['specCharChance', 'float', 0.17]
CLEAR_FLAG = ['clearOnExit','int', 1]
IPFS_ADDRESS = ['ipfsAddress', 'str', '']
METHOD_CALL_KEYS = ['generateNewPW', 'createVaultTable','printVaultTable','updateVaultTable',
'uploadToIPFS', 'printVaultTableIPFS', 'delVaultTableRecord', 'createShortcut', 'quit']

#arg[0] = cmd, argv[1] = callableMethod dict, argv[2] = vaultObj, argv[3] = keyObj, argv[4] = configOb
def runMethod(*argv):
    '''Run method if found in callableMethod dict'''
    for methods in argv[4].getMethodsKeyIter('method'):     
        if argv[0].lower() == methods[0].lower():
            if methods[1] in argv[1]:
                argv[1][methods[1]](argv[2],argv[3],argv[4])
            else:
                print('\nERROR: Method "{}" not found. Please update config.xml or revert to default.xml\n'.format(methods[1]))
            return 1
    return 0

def exit(*argv):
    '''exit console'''
    tmp = argv[2].getElem(CLEAR_FLAG[0],CLEAR_FLAG[1])
    if tmp == 1:
        os.system('clear') if OS == 'unix' else os.system('cls')
    elif CLEAR_FLAG[2] and tmp != 1 and tmp != 0:
        os.system('clear') if OS == 'unix' else os.system('cls')
    garb = gc.collect()
    quit()

def getDecryptedVaultTable(*argv):
	'''Return decrypted bytestring as json'''
	if argv[0].checkFile():
		return json.loads(argv[1].decryptByteString(argv[0].readFile()))
	return None

def createShortcut(*argv):
    '''Create bash script running script + arg, then a symbolic link to script'''
    if OS == 'unix':
        bashFile = bash(read('\nInput bash script path\n'),SCRIPT_PATH[0] + '/tmp.sh')
        pythonCmd = 'python' if PYTHON_VERSION == '2' else 'python3'
        bashFile.writeFile('#! /bin/bash\n{0} {1}/{2} -m={3}'.format(pythonCmd,SCRIPT_PATH[0],os.path.basename(__file__),read('\nInput shortcut method\n')),'w+')
        bashFile.createShortcut(read('\nInput shortcut path\n'))
    else:
        print('\nERROR: only supported on linux (for now)....\n')

def delVaultTableRecord(*argv):
    '''Delete record from vault table by user input keyname'''
    tmp = getDecryptedVaultTable(*argv) 
    if tmp:
        siteAlias = read('which site alias to delete? (i.e. "reddit")\n')
        check = read('\nAre you sure? Can not be undone [y/n]?\n')
        if check[0].lower() == 'y':
            try:
                tmp['passwords'].pop(str(siteAlias))
                print('\n{} record deleted....\n'.format(siteAlias))
                argv[0].writeFile(argv[1].encryptByteString(bytes(json.dumps(tmp), 'utf-8')),'wb')
            except KeyError:
                print('\nERROR: {} is not an alias in vault\n'.format(siteAlias))
    else:
        print('\nERROR: Table not found at {}\n'.format(argv[0].getFilePath()))

def updateVaultTable(*argv):
    '''Add/update vault keypair based on given user input'''
    tmp = getDecryptedVaultTable(*argv)
    if tmp:
        siteAlias = read('site alias? (i.e. "reddit")\n')
        pw = read('enter pw:\n')
        tmp['passwords'][siteAlias] = pw
        try:
            argv[0].writeFile(argv[1].encryptByteString(bytes(json.dumps(tmp), 'utf-8')),'wb')
        except (IOError, ValueError) as e:
            print(e)
    else:
        print('\nERROR: Table not found at {}\n'.format(argv[0].getFilePath()))        

def printVaultTableIPFS(*argv):
    '''Print JSON of Vault Table on IPFS (from referenced address in config.xml)'''
    tmp = None
    IPFSaddress = argv[2].getElem(IPFS_ADDRESS[0],IPFS_ADDRESS[1])
    if IPFS and IPFSaddress:
        if len(IPFSaddress) == 46:
            print('\nreading from IPFS....\n')
            client = IPFS.connect()
            tmp = argv[1].decryptByteString(client.cat(IPFSaddress))
            client.close()
            if tmp:
                if sys.version_info[0] == 2:
                    print(json.loads(tmp))
                else:
                    print(json.dumps(json.loads(tmp),sort_keys=True,indent=4))
    else:
        print('\nERROR: No IPFS address found in {}'.format(argv[2].getFilePath()))

def printVaultTable(*argv):
    '''Print JSON of Vault Table'''
    tmp = None
    if argv[0].checkFile():
        tmp = argv[1].decryptByteString(argv[0].readFile())   
    if tmp:
        if PYTHON_VERSION == '2':
            print(json.loads(tmp))
        else:
            print(json.dumps(json.loads(tmp),sort_keys=True,indent=4))
    else:
        print('\nERROR: Table not found at {}\n'.format(argv[0].getFilePath()))

def uploadToIPFS(*argv):
    '''Upload encrypted JSON to IPFS if running IPFS node'''
    if IPFS:
        uploadOption = read('Upload to IPFS? [y/n]: ')
        if uploadOption.lower() == 'y':
            if argv[0].checkFile():
                client = IPFS.connect()
                IPFSaddress = argv[2].getElem(IPFS_ADDRESS[0],IPFS_ADDRESS[1])
                if IPFSaddress:
                    if len(IPFSaddress) == 46 and client.pin.ls(IPFSaddress):
                        client.pin.rm(IPFSaddress)
                res = client.add(SCRIPT_PATH[0] + DEFAULT_VAULT_PATH[0])
                argv[2].updateElem('ipfsAddress', res['Hash'])
                print('\nNew CID: {}\n'.format(res['Hash']))
                client.pin.add(res['Hash'])
                client.close()
    else:
        print('\nERROR: ipfshttpclient module not installed....\n')

def read(prompt):
    '''Call raw_input() or input() depending on running python version'''
    if sys.version_info[0] == 2:
        return raw_input(prompt)
    return input(prompt)

def overwriteVault(*argv):
	'''Validate that user wants to overwrite vault'''
	inputMsg = '\t!!!! WARNING: This will overwrite vault at {0}{1} \nContinue? [y/n]: '.format(SCRIPT_PATH[0],DEFAULT_VAULT_PATH[0])
	userInput = read(inputMsg)
	if userInput.lower() == 'y':
		argv[1].rmFile()
		argv[0].rmFile()
		print('\n{0} and {1} removed....\n'.format(argv[0].getFilePath(),argv[1].getFilePath()))
		return 1
	else:
		print('\nVault not created\n')
		return 0

def createVaultTable(*argv):
    '''Create vault with default values at default location'''
    mkVaultBool = 1
    if os.path.exists(VAULT_PATH[2]):
    	mkVaultBool = overwriteVault(*argv)
    if mkVaultBool:
        argv[0].mkDir() if not argv[0].checkParentDir() else None
        argv[1].mkDir() if not argv[1].checkParentDir() else None
        print(VAULT_PATH[2])
        vaultObj = VT(None,VAULT_PATH[2])
        keyObj = VK(None,SCRIPT_PATH[0] + DEFAULT_HIDE_PATH[0])
        keyObj.generateVaultKey()
        tmp = { "passwords" : { } }
        vaultObj.writeFile(keyObj.encryptByteString(bytes(json.dumps(tmp), 'utf-8')),'wb')
        argv[2].updateElem(VAULT_PATH[0],vaultObj.getFilePath())
        print('\nVault created at {}\n'.format(vaultObj.getFilePath()))

def hashInputPlusSalt(*argv):
    '''Get sha256 of password seed + salt'''
    specialChars = ['!','@','#','$','%','^','&','*','(',')','+','=','-','~','_',' ']
    tmp = hashlib.sha256((argv[0] + str(argv[1])).encode()).hexdigest()
    tmp2 = ""
    for char in tmp:
        if random.random() < argv[2]:
            tmp2 += "".join(random.choice([random.choice(specialChars),char]))
        else:
            tmp2 += "".join(random.choice([char.upper(),char]))
    return tmp2

def generateNewPW(*argv):
    '''Prompt for password seed and generate random sha256'''
    tmp1 = argv[2].getElem(HASH_LIST_LEN[0],HASH_LIST_LEN[1])
    if tmp1:
    	hashListSize = tmp1 if tmp1 > 1 else HASH_LIST_LEN[2]
    else:
    	hashListSize = HASH_LIST_LEN[2]
    index = int(round(random.randrange(0,hashListSize - 1)))
    i = 0
    hashList = []
    startTime = time.perf_counter()
    tmp2 = argv[2].getElem(SPEC_CHAR_CHANCE[0],SPEC_CHAR_CHANCE[1])
    while i < hashListSize:
        saltObj = salt()
        hashList.append(hashInputPlusSalt('tmp',saltObj.getSalt(),tmp2)) if tmp2 else hashList.append(hashInputPlusSalt('tmp',saltObj.getSalt(),SPEC_CHAR_CHANCE[2]))
        i += 1
    print('\n{0}: {1} hashes in {2} seconds....\n\nNew password: {3}'.format(platform.processor(),i,time.perf_counter() - startTime,hashList[index]))

def setCallableMethods():
    '''Set user-callable methods dict'''
    tmp = {}
    tmp[METHOD_CALL_KEYS[0]] = generateNewPW
    tmp[METHOD_CALL_KEYS[1]] = createVaultTable
    tmp[METHOD_CALL_KEYS[2]] = printVaultTable
    tmp[METHOD_CALL_KEYS[3]] = updateVaultTable
    tmp[METHOD_CALL_KEYS[4]] = uploadToIPFS
    tmp[METHOD_CALL_KEYS[5]] = printVaultTableIPFS
    tmp[METHOD_CALL_KEYS[6]] = delVaultTableRecord
    tmp[METHOD_CALL_KEYS[7]] = createShortcut
    tmp[METHOD_CALL_KEYS[8]] = exit
    return tmp

def setOptionString(configObj):
	'''Set and return user menu string'''
	mainMethods = configObj.getMethodsKeyIter('desc')
	optionString = '\n==passGen==\n\nOptions:'
	for elem in mainMethods:
	    optionString += '\n{0} = {1}'.format(elem[0],elem[1])
	optionString += '\nInput command: '
	return optionString

def getArgs():
    '''Get script args'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-k','--key')
    parser.add_argument('-c','--config')
    parser.add_argument('-m','--method')
    return parser.parse_args()

#TO-DO: clear args.key if new vault created on last iteration
def main():
	'''Run method based on user-input if option keypair found in config.xml'''
	args = getArgs()
	while 1:
		configs = [config(args.config, SCRIPT_PATH[0] + DEFAULT_CONFIG_PATH[0])]
		vaultKeys = [VK(args.key, SCRIPT_PATH[0] + DEFAULT_HIDE_PATH[0])]
		vaults = [VT(configs[0].getElem(VAULT_PATH[0],VAULT_PATH[1]),VAULT_PATH[2])]
		optionString = setOptionString(configs[0])
		cmd = args.method if args.method else read(optionString)
		print('\nERROR: Command "{}" not found\n'.format(cmd)) if not runMethod(cmd,setCallableMethods(),vaults[0],vaultKeys[0],configs[0]) else None
		args.method = None
 
if __name__ == '__main__':
    main()
    