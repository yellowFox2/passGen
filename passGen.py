#WISHLIST: iOS/Android interface -- need to refactor for ReactJS (?), optionally host encrypted vault on IPFS -- decrypt on client-side
import hashlib, random, sys, argparse, os, json
import xml.etree.ElementTree as ET
from getpass import getpass as gp
from src.salt import salt
from src.vaultTable import vaultTable as VT
from src.vaultKey import vaultKey as VK
from src.config import config

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__)).replace('\\','/')
DEFAULT_HIDE_PATH = '/.hide/vault.key'
DEFAULT_VAULT_PATH = '/.vault/vault.json'
DEFAULT_CONFIG_PATH = '/config/config.xml'

#TO-DO: remove need for try block
def runMethod(iterObj,userInput,mainMethods,vaultObj,keyObj,configObj):
    '''Run method if found in callableMethod dict'''
    for options in iterObj:     
        if userInput.lower() == options[0].lower():
            if options[1] in mainMethods:
                mainMethods[options[1]](vaultObj,keyObj,configObj)
            else:
                print('\nERROR: Method "{}" not found. Please update config.xml\n'.format(options[1]))
            return 1
    return 0

def getArgs():
    '''Get script args'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-k','--key')
    parser.add_argument('-c','--config')
    return parser.parse_args()

def exit(*argv):
    quit()

def updateVaultTable(*argv):
    '''Add/update vault keypair based on given user input'''
    if argv[0].checkFile():
        tmp = json.loads(argv[1].decryptByteString(argv[0].readFile()))
        siteAlias = read('site alias? (i.e. "reddit")\n')
        pw = read('enter pw:\n')
        tmp['passwords'][siteAlias] = pw
        try:
            argv[0].writeFile(argv[1].encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
        except (IOError, ValueError) as e:
            print(e)
    else:
        print('\nERROR: Table not found at {}\n'.format(argv[0].getFilePath()))

def printVaultTable(*argv):
    '''Print JSON of Vault Table'''
    if argv[0].checkFile():
        tmp = argv[1].decryptByteString(argv[0].readFile())
        if tmp:
            if sys.version_info[0] == 2:
                print(json.loads(tmp))
            else:
                print(json.dumps(json.loads(tmp),sort_keys=True,indent=4))
        else:
            print('\nERROR: couldnt find key at {}'.format(argv[1].getFilePath()))
    else:
        print('\nERROR: Table not found at {}\n'.format(argv[0].getFilePath()))

def read(prompt):
    '''Call raw_input() or input() depending on running python version'''
    if sys.version_info[0] == 2:
        return raw_input(prompt)
    return input(prompt)

#TO-DO: Cleanup + remove redundancy
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
        tmp = { "passwords" : { "tmp" : "none" } }
        vaultObj.writeFile(keyObj.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
        print('\nvault created at {}/.vault\n'.format(SCRIPT_PATH))

#TO-DO: add special chars + random capitilization
def hashInputPlusSalt(userInput,saltVal):
    '''Get sha256 of password seed + salt'''
    return hashlib.sha256((userInput + str(saltVal)).encode()).hexdigest()

#TO-DO: make literalHashTable size configurable + improve hash selection procedure
def generateNewPW(*argv):
    '''Prompt for password seed and generate random sha256'''
    tmp = gp('\nEnter password seed: ')
    index = int(round(random.randrange(0,999)))
    i = 0
    literalHashTable = []
    while i < 1000:
        saltObj = salt()
        literalHashTable.append(hashInputPlusSalt(tmp,saltObj.getSalt()))
        i += 1
    print('\nNew password: {}'.format(literalHashTable[index]))

def setCallableMainMethods():
    '''Set user-callable methods dict'''
    tmp = {}
    tmp['generateNewPW'] = generateNewPW
    tmp['createVaultTable'] = createVaultTable
    tmp['printVaultTable'] = printVaultTable
    tmp['updateVaultTable'] = updateVaultTable
    tmp['quit'] = exit
    return tmp

def main():
    '''Run method based on user-input if option keypair found in config.xml'''
    callableMethods = {}
    callableMethods = setCallableMainMethods()
    args = getArgs()
    config0 = config(args.config, SCRIPT_PATH + DEFAULT_CONFIG_PATH)
    vaultKey = VK(args.key, SCRIPT_PATH + DEFAULT_HIDE_PATH)     
    vault = VT(config0, SCRIPT_PATH + DEFAULT_VAULT_PATH)
    #TO-DO: import optionString from config.xml
    optionString = '\n==passGen==\n\nOptions:\ngenPass = generate 64 char password'
    optionString += '\nvaultInit = create new vault\ngetVault = read vault values'
    optionString += '\nupdateVault = add vault value\nquit = close session\n\nInput command: ' 
    while 1:
        cmd = read(optionString)
        print('\nERROR: Command "{}" not found\n'.format(cmd)) if not runMethod(iter(config0.getMethods().items()),cmd,callableMethods,vault,vaultKey,config0) else None
                
if __name__ == '__main__':
    main()
    