import os, json, sys
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet
from .vaultKey import vaultKey as VK
from .file import file

class vaultTable(file):

    def read(self,prompt):
        '''Call raw_input() or input() depending on running python version'''
        if sys.version_info[0] == 2:
            return raw_input(prompt)
        return input(prompt)
          
    def encryptByteString(self,inputString):
        '''Encrypt a bytes object -- convert a string to bytes first -- using user referenced vault key'''
        f = Fernet(self.vaultKey.readFile())
        return f.encrypt(inputString)
        
    def updateVaultTable(self):
        '''Add/update vault keypair based on given user input'''
        siteAlias = self.read('site alias? (i.e. "reddit")\n')
        tmp = self.getVaultTable()
        pw = self.read('enter pw:\n')
        tmp['passwords'][siteAlias] = pw
        try:
            self.writeFile(self.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
        except (IOError, ValueError) as e:
            print(e)      

    def printVaultTable(self):
        '''Print vault to console'''
        if self.getVaultTable():
            if sys.version_info[0] == 2:
                print(self.getVaultTable())
            else:
                print(json.dumps(self.getVaultTable(),sort_keys=True,indent=4))

    def createVaultTable(self):
        '''Create vault with default values at default location'''
        createVaultBool = True      
        if os.path.exists(self.getRelScriptPath() + '/.vault/vault.json'):
            print('!!!! WARNING: a vault already exists at {}/.vault/vault.json'.format(self.getRelScriptPath()))
            inputMsg = 'Continue? This will overwrite vault existing at ' 
            inputMsg += self.getRelScriptPath() 
            inputMsg += '/.vault/vault.json [y/n]: '
            option = self.read(inputMsg)
            if option.lower() == 'y':
                os.remove(self.getRelScriptPath() + '/.hide/vault.key') if os.path.exists(self.getRelScriptPath() + '/.hide/vault.key') else None         
                os.remove(self.getRelScriptPath() + '/.vault/vault.json') if os.path.exists(self.getRelScriptPath() + '/.vault/vault.json') else None            
            elif option.lower() == 'n':
                createVaultBool = False
                print('Aborting vault creation....\n')
            else:
                createVaultBool = False
                print('No option selected')      
        if createVaultBool is True:
            tmp = { "passwords" : {"tmp":"none"} }
            os.mkdir(self.getRelScriptPath() + '/.vault') if not os.path.exists(self.getRelScriptPath() + '/.vault') else None
            os.mkdir(self.getRelScriptPath() + '/.hide') if not os.path.exists(self.getRelScriptPath() + '/.hide') else None
            self.vaultKey = VK(self.getRelScriptPath() + '/.hide/vault.key')
            self.setFilePath(self.getRelScriptPath() + '/.vault/vault.json')
            self.vaultKey.generateVaultKey()
            self.writeFile(self.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
            print('\nvault created at {}/.vault\n'.format(self.getRelScriptPath()))
 
    def setVaultKey(self):
        '''Set vault key reference'''
        if self.args.key is not None:
                self.vaultKey = VK(self.args.key)
        else:
            self.vaultKey = VK(self.getRelScriptPath() + '/.hide/vault.key')
    
    def getVaultKey(self):
        return self.vaultKey

    def setVaultPath(self):
        '''Set vault path to object attribute'''
        if self.args.config:
            if os.path.exists(self.args.config):
                xml = ET.parse(self.args.config)
                root = xml.getroot()
                if os.path.exists(root[0].text):
                    super().__init__(root[0].text)
                    return
            print('ERROR: config path given as arg != valid path\n')
            return
        super().__init__(self.getRelScriptPath() + '/.vault/vault.json')
        
    def getVaultTable(self):
        '''Return JSON of decrypted vault'''
        try:
            f = Fernet(self.vaultKey.readFile())
            decrypted = f.decrypt((self.readFile()))
            return json.loads(decrypted)
        except (IOError, ValueError) as e:
            print(e)
        
    def setRelScriptPath(self,path):
        self.relScriptPath = path
        
    def getRelScriptPath(self):
        return self.relScriptPath
        
    def setArgs(self,args):
        self.args = args
        
    def getArgs(self):
        return self.args
    
    def __init__(self,args,scriptPath):
        self.setRelScriptPath(scriptPath)
        self.setArgs(args)
        self.setVaultPath()
        self.setVaultKey()
        