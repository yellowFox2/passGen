#WISHLIST: iOS/Android interface -- need to refactor for ReactJS (?), optionally host encrypted vault on IPFS -- decrypt on client-side
import hashlib, random, sys, argparse, os, json
import xml.etree.ElementTree as ET
from getpass import getpass as gp
from src.salt import salt
from src.vaultTable import vaultTable as VT
from src.vaultKey import vaultKey as VK

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

#TO-DO: remove need for try block
def runMethod(iterObj,userInput,mainMethods,vaultObj,keyObj):
    '''Run method if found in callableMethod dict'''
    for options in iterObj:     
        if userInput.lower() == options[0].lower():
            if options[1] in mainMethods:
                try:
                    mainMethods[options[1]]()
                except TypeError:
                    mainMethods[options[1]](vaultObj,keyObj)
            else:
                print('\nERROR: Method "{}" not found. Please update config.xml\n'.format(options[1]))
            return 1
    return 0

#TO-DO: return dictionary instead of list + optimize (?)   
def getConfigOptions(xmlPath):
    '''Retrieve user option elements from XML as dict'''
    xml = ET.parse(xmlPath)
    root = xml.getroot()
    options = root.findall("./options/option")
    optionsList = []
    for option in options:
        optionsList.append(option.attrib)
    tmp = {}
    for keyPair in optionsList:
        tmp[keyPair['name']] = keyPair['method']      
    return tmp

def getArgs():
    '''Get script args'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-k','--key')
    parser.add_argument('-c','--config')
    return parser.parse_args()

def updateVaultTable(vaultObj,keyObj):
    '''Add/update vault keypair based on given user input'''
    tmp = json.loads(keyObj.decryptByteString(vaultObj.readFile()))
    if tmp:
        siteAlias = read('site alias? (i.e. "reddit")\n')
        pw = read('enter pw:\n')
        tmp['passwords'][siteAlias] = pw
        try:
            vaultObj.writeFile(keyObj.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
        except (IOError, ValueError) as e:
            print(e)
    else:
        print('\nERROR: Table not found at {}\n'.format(vaultObj.getFilePath()))

def printVaultTable(vaultObj,keyObj):
    '''Print JSON of Vault Table'''
    tmp = keyObj.decryptByteString(vaultObj.readFile())
    if tmp:
        if sys.version_info[0] == 2:
            print(json.loads(tmp))
        else:
            print(json.dumps(json.loads(tmp),sort_keys=True,indent=4))
    else:
        print('\nERROR: couldnt find key at {}'.format(keyObj.getFilePath()))

def read(prompt):
    '''Call raw_input() or input() depending on running python version'''
    if sys.version_info[0] == 2:
        return raw_input(prompt)
    return input(prompt)

#TO-DO: Cleanup + remove redundancy
def createVaultTable(vaultObj,keyObj):
        '''Create vault with default values at default location'''
        createVaultBool = True      
        if os.path.exists(SCRIPT_PATH + '/.vault/vault.json'):
            print('!!!! WARNING: a vault already exists at {}/.vault/vault.json'.format(SCRIPT_PATH))
            inputMsg = 'Continue? This will overwrite vault existing at ' 
            inputMsg += SCRIPT_PATH 
            inputMsg += '/.vault/vault.json [y/n]: '
            option = read(inputMsg)
            if option.lower() == 'y':
                os.remove(SCRIPT_PATH + '/.hide/vault.key') if os.path.exists(SCRIPT_PATH + '/.hide/vault.key') else None         
                os.remove(SCRIPT_PATH + '/.vault/vault.json') if os.path.exists(SCRIPT_PATH + '/.vault/vault.json') else None            
            elif option.lower() == 'n':
                createVaultBool = False
                print('Aborting vault creation....\n')
            else:
                createVaultBool = False
                print('No option selected')      
        if createVaultBool is True:
            os.mkdir(SCRIPT_PATH + '/.vault') if not os.path.exists(SCRIPT_PATH + '/.vault') else None
            os.mkdir(SCRIPT_PATH + '/.hide') if not os.path.exists(SCRIPT_PATH + '/.hide') else None
            vaultObj = VT(None,SCRIPT_PATH)
            keyObj = VK(SCRIPT_PATH + '/.hide/vault.key')
            keyObj.generateVaultKey()
            tmp = { "passwords" : { "tmp" : "none" } }
            vaultObj.writeFile(keyObj.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
            print('\nvault created at {}/.vault\n'.format(SCRIPT_PATH))

#TO-DO: add special chars + random capitilization
def hashInputPlusSalt(userInput,saltVal):
    '''Get sha256 of password seed + salt'''
    return hashlib.sha256((userInput + str(saltVal)).encode()).hexdigest()

#TO-DO: make literalHashTable size configurable + improve hash selection procedure
def generateNewPW():
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
    tmp['quit'] = quit
    return tmp

def main():
    '''Run method based on user-input if option keypair found in config.xml'''
    callableMethods = {}
    callableMethods = setCallableMainMethods()
    args = getArgs()
    if args.key and os.path.exists(args.key):
        vaultKey = VK(args.key)
    else:
        vaultKey = VK(SCRIPT_PATH + '/.hide/vault.key')
    vault = VT(args,SCRIPT_PATH) 
    while 1:
        #TO-DO: import optionString from config.xml
        optionString = '\n==passGen==\n\nOptions:\ngenPass = generate 64 char password'
        optionString += '\nvaultInit = create new vault\ngetVault = read vault values'
        optionString += '\nupdateVault = add vault value\nquit = close session\n\nInput command: '
        cmd = read(optionString)
        options = {}
        if args.config:
            options = getConfigOptions(args.config).items()
        else:
            options = getConfigOptions((vault.getRelScriptPath() + '/config/config.xml')).items()
        optionsIter = iter(options)
        print('\nERROR: Command "{}" not found\n'.format(cmd)) if not runMethod(optionsIter,cmd,callableMethods,vault,vaultKey) else None
                
if __name__ == '__main__':
    main()
    