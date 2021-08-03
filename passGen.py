import hashlib, random, sys, argparse, os, json, time, platform, gc
import xml.etree.ElementTree as ET
from src.salt import salt
from src.vaultTable import vaultTable as VT
from src.vaultKey import vaultKey as VK
from src.config import config
try:
    import ipfshttpclient as IPFS
except ImportError:
    IPFS = None

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
DEFAULT_HIDE_PATH = '/.hide/vault.key'
DEFAULT_VAULT_PATH = '/.vault/vault.json'
DEFAULT_CONFIG_PATH = '/config/config.xml'

def runMethod(*argv):
    '''Run method if found in callableMethod dict'''
    for options in argv[4].getMethodsKeyIter('method'):     
        if argv[0].lower() == options[0].lower():
            if options[1] in argv[1]:
                argv[1][options[1]](argv[2],argv[3],argv[4])
            else:
                print('\nERROR: Method "{}" not found. Please update config.xml\n'.format(options[1]))
            return 1
    return 0

def exit(*argv):
    garb = gc.collect()
    quit()

def getDecryptedVaultTable(*argv):
    '''Return decrypted bytestring as json'''
    if argv[0].checkFile():
        return json.loads(argv[1].decryptByteString(argv[0].readFile()))
    return None

def delVaultTableRecord(*argv):
    '''Delete record from vault table by user input keyname'''
    tmp = getDecryptedVaultTable(*argv) 
    if tmp:
        siteAlias = read('which site alias to delete? (i.e. "reddit")\n')
        check = read('\nAre you sure? Can not be undone [y/n]?\n')
        if check[0].lower() == 'y':
            tmp['passwords'].pop(str(siteAlias))
            print('\n{} record deleted....\n'.format(siteAlias))
            argv[0].writeFile(argv[1].encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
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
            argv[0].writeFile(argv[1].encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
            uploadToIPFS(*argv) if IPFS else None
        except (IOError, ValueError) as e:
            print(e)
    else:
        print('\nERROR: Table not found at {}\n'.format(argv[0].getFilePath()))        


def printVaultTableIPFS(*argv):
    '''Print JSON of Vault Table on IPFS (from referenced address in config.xml)'''
    tmp = None
    IPFSaddress = argv[2].getIPFSaddress()
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
        if sys.version_info[0] == 2:
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
                IPFSaddress = argv[2].getIPFSaddress()
                if len(IPFSaddress) == 46 and client.pin.ls(IPFSaddress):
                    client.pin.rm(IPFSaddress)
                res = client.add(SCRIPT_PATH + DEFAULT_VAULT_PATH)
                argv[2].updateIPFSaddress(res['Hash'])
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

#TO-DO: Cleanup
def createVaultTable(*argv):
    '''Create vault with default values at default location'''
    mkVaultBool = True
    if argv[0].checkFile():
        inputMsg = '\t!!!! WARNING: This will overwrite vault at {0}{1} \nContinue? [y/n]: '.format(SCRIPT_PATH,DEFAULT_VAULT_PATH)
        userInput = read(inputMsg)
        if userInput.lower() == 'y':
            mkVaultBool = True
            argv[1].rmFile()
            argv[0].rmFile()
        elif userInput.lower() == 'n':
            mkVaultbool = False
            print('\nVault not created\n')
        else:
            mkVaultbool = False
            print('No option selected')
    if mkVaultBool:
        argv[0].mkDir() if not argv[0].checkParentDir() else None
        argv[1].mkDir() if not argv[1].checkParentDir() else None
        vaultObj = VT(argv[2],SCRIPT_PATH + DEFAULT_VAULT_PATH)
        keyObj = VK(None,SCRIPT_PATH + DEFAULT_HIDE_PATH)
        keyObj.generateVaultKey()
        tmp = { "passwords" : { } }
        vaultObj.writeFile(keyObj.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
        print('\nvault created at {}/.vault\n'.format(SCRIPT_PATH))
        uploadToIPFS(*argv)

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
    index = int(round(random.randrange(0,argv[2].getHashListSize() - 1)))
    i = 0
    hashList = []
    startTime = time.perf_counter()
    while i < argv[2].getHashListSize():
        saltObj = salt()
        hashList.append(hashInputPlusSalt('tmp',saltObj.getSalt(),argv[2].getSpecCharChance()))
        i += 1
    print('\n{0}: {1} hashes in {2} seconds....\n\nNew password: {3}'.format(platform.processor(),i,time.perf_counter() - startTime,hashList[index]))

def setCallableMethods():
    '''Set user-callable methods dict'''
    tmp = {}
    tmp['generateNewPW'] = generateNewPW
    tmp['createVaultTable'] = createVaultTable
    tmp['printVaultTable'] = printVaultTable
    tmp['updateVaultTable'] = updateVaultTable
    tmp['uploadToIPFS'] = uploadToIPFS
    tmp['printVaultTableIPFS'] = printVaultTableIPFS
    tmp['delVaultTableRecord'] = delVaultTableRecord
    tmp['quit'] = exit
    return tmp

def getOptionDescs(configObj):
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
    return parser.parse_args()

def main():
    '''Run method based on user-input if option keypair found in config.xml'''
    args = getArgs()
    configs = []
    vaultKeys = []
    vaults = []
    configs.append(config(args.config, SCRIPT_PATH + DEFAULT_CONFIG_PATH))
    vaultKeys.append(VK(args.key, SCRIPT_PATH + DEFAULT_HIDE_PATH))
    vaults.append(VT(configs[0], SCRIPT_PATH + DEFAULT_VAULT_PATH))
    while 1:
        optionString = getOptionDescs(configs[0])        
        cmd = read(optionString)
        print('\nERROR: Command "{}" not found\n'.format(cmd)) if not runMethod(cmd,setCallableMethods(),vaults[0],vaultKeys[0],configs[0]) else None
                
if __name__ == '__main__':
    main()
    