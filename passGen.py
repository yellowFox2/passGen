import hashlib, random, sys, argparse, os
import xml.etree.ElementTree as ET
from getpass import getpass as gp
from src.salt import salt
from src.vaultTable import vaultTable

def runMethod(iterObj,userInput,mainMethods,classObj):
    for options in iterObj:     
        if userInput == options[0]:
            if options[1] in mainMethods:
                mainMethods[options[1]]()
                return 1
            elif options[1] in dir(classObj):
                getattr(classObj,options[1])()
                return 1
            else:
                print('\nERROR: Method "{}" not found. Please update config.xml\n'.format(options[1]))
                return 1
    return 0
    
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

def hashInputPlusSalt(userInput,saltVal):
    '''Get sha256 of password seed + salt'''
    return hashlib.sha256((userInput + str(saltVal)).encode()).hexdigest()

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
    tmp['quit'] = quit
    return tmp

def main():
    '''Run method based on user-input if option keypair found in config.xml'''
    callableMethods = {}
    callableMethods = setCallableMainMethods()
    args = getArgs()
    vault = vaultTable(args,os.path.dirname(os.path.abspath(__file__)))
    while 1:
        optionString = '\n==passGen==\n\nOptions:\ngenPass = generate 64 char password'
        optionString += '\nvaultInit = create new vault\ngetVault = read vault values'
        optionString += '\nupdateVault = add vault value\nquit = close session\n\nInput command: '
        cmd = vault.read(optionString)
        options = {}
        if args.config:
            options = getConfigOptions(args.config).items()
        else:
            options = getConfigOptions((vault.getRelScriptPath() + '/config/config.xml')).items()
        optionsIter = iter(options)
        print('\nERROR: Command "{}" not found\n'.format(cmd)) if not runMethod(optionsIter,cmd,callableMethods,vault) else None
                
if __name__ == '__main__':
    main()
    