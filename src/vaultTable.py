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
        tmp = self.getVaultTable()
        if not tmp is None:
            siteAlias = self.read('site alias? (i.e. "reddit")\n')
            pw = self.read('enter pw:\n')
            tmp['passwords'][siteAlias] = pw
            try:
                self.writeFile(self.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
            except (IOError, ValueError) as e:
                print(e)
        else:
            print('\nERROR: Table not found at {}\n'.format(self.getFilePath()))

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
            self.setVaultTable()
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
        super().__init__(self.getRelScriptPath() + '/.vault/vault.json')
    
    def setVaultTable(self):
        '''Return JSON of decrypted vault'''
        try:
            vaultKeyVal = self.vaultKey.readFile()
            if vaultKeyVal:          
                f = Fernet(vaultKeyVal)
                vaultVal = self.readFile()
                if vaultVal:
                    decrypted = f.decrypt(vaultVal)
                    self.vaultTable = json.loads(decrypted)
                    return
            self.vaultTable = None
        except (IOError, ValueError) as e:
            print(e)
            
    def getVaultTable(self):
        return self.vaultTable
        
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
        self.setVaultTable()
        
    def __str__(self):
        '''Print vault to console'''
        if not self.getVaultTable() is None:
            if sys.version_info[0] == 2:
                return self.getVaultTable()
            else:
                return json.dumps(self.getVaultTable(),sort_keys=True,indent=4)
        else:
            return '\nERROR: Table not found at {}\n'.format(self.getFilePath())
        