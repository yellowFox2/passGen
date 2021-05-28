import hashlib, random, sys, os, argparse, json
from salt import salt
from vaultTable import vaultTable
from getpass import getpass as gp
import xml.etree.ElementTree as ET

def hashInputPlusSalt(userInput,saltVal):
	return hashlib.sha256((userInput + str(saltVal)).encode()).hexdigest()

def generateNewPW():
	tmp = gp('Enter password seed: ')
	index = int(round(random.randrange(0,999)))
	i = 0
	literalHashTable = []
	while i < 1000:
		saltObj = salt()
		literalHashTable.append(hashInputPlusSalt(tmp,saltObj.getSalt()))
		i += 1
	print('New password: ',literalHashTable[index])

def parseXML(xmlPath):
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
    nextIter = True
    foundBool = True
    vault = vaultTable(getArgs())
    while(1):
        cmd = read('\n==passGen==\n\nOptions:\ngenPass = generate 64 char password\nvaultInit = create new vault\ngetVault = read vault values\nupdateVault = add vault value\nquit = close session\n\nInput command: ')
        options = {}
        options = parseXML((vault.getRelScriptPath() + '\config\\config.xml')).items()
        optionsIter = iter(options)
        for options in optionsIter:
            if cmd == 'genPass':
                generateNewPW()
                break
            elif cmd == 'quit':
                nextIter = False
                break
            elif cmd == options[0]:
                if not cmd == 'genPass' or not cmd == 'quit':
                    getattr(vault,options[1])()
                    foundBool = True
                    break
            else:
                foundBool = False
        if not foundBool:
            print('\nERROR: Command not found\n') 
        if not nextIter:
            break
if __name__ == '__main__':
    main()