import hashlib, random, sys, argparse
import xml.etree.ElementTree as ET
from getpass import getpass as gp
from salt import salt
from vaultTable import vaultTable

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
    print('\nNew password: ',literalHashTable[index])

def parseXML(xmlPath):
    '''Retrieve user option elements from XML as dict'''
    xml = ET.parse(xmlPath)
    root = xml.getroot()
    options = root.findall("./options/option")
    optionsList = []
    for option in options:
        optionsList.append(option.attrib)
    tmp = {}
    for keyPair in optionsList:
        tmp[keyPair['name']] = keyPair['function']      
    return tmp

def getArgs():
    '''Get script args'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-k','--key')
    parser.add_argument('-c','--config')
    return parser.parse_args()
    
def setCallableFunctions():
    '''Set user-callable functions dict'''
    tmp = {}
    tmp['generateNewPW'] = generateNewPW
    tmp['quit'] = quit
    return tmp

def main():
    '''Run function based on user-input if option keypair found in config.xml'''
    callableFunctions = {}
    callableFunctions = setCallableFunctions()
    optionFoundBool = True
    args = getArgs()
    vault = vaultTable(args)
    while 1:
        optionString = '\n==passGen==\n\nOptions:\ngenPass = generate 64 char password'
        optionString += '\nvaultInit = create new vault\ngetVault = read vault values'
        optionString += '\nupdateVault = add vault value\nquit = close session\n\nInput command: '
        cmd = vault.read(optionString)
        options = {}
        if args.config:
            options = parseXML(args.config).items()
        else:
            options = parseXML((vault.getRelScriptPath() + '/config/config.xml')).items()
        optionsIter = iter(options)
        for options in optionsIter:
            if cmd == options[0]:
                try:
                    getattr(vault,options[1])()
                except AttributeError:
                    callableFunctions[options[1]]()
                optionFoundBool = True
                break
            optionFoundBool = False
        if not optionFoundBool:
            print('\nERROR: Command not found\n')
if __name__ == '__main__':
    main()
    