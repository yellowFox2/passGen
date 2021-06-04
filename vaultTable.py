import os, json, sys
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet

class vaultTable:
    def read(self,prompt):
        '''Call raw_input() or input() depending on running python version'''
        if sys.version_info[0] == 2:
            return raw_input(prompt)
        return input(prompt)
          
    def encryptByteString(self,inputString):
        '''Encrypt a bytes object -- convert a string to bytes first -- using user referenced vault key'''
        f = Fernet(self.readFile(self.getVaultKeyPath()))
        return f.encrypt(inputString)
        
    def updateVaultTable(self):
        '''Add/update vault keypair based on given user input'''
        if not os.path.exists(self.getVaultKeyPath()):
            print('ERROR: No vault key found at ', self.getVaultKeyPath())
        else:
            siteAlias = self.read('site alias? (i.e. "reddit")\n')
            tmp = self.getVaultTable()
            pw = self.read('enter pw:\n')
            tmp['passwords'][siteAlias] = pw
            try:
                self.writeFile(self.getVaultPath(),self.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
            except (IOError, ValueError) as e:
                print(e.errno)
                print(e)

    def printVaultTable(self):
        '''Print vault to console'''
        if self.getVaultTable():
            try:
                print(json.dumps(self.getVaultTable(),sort_keys=True,indent=4))
            except ValueError:
                print(self.getVaultTable())
           
    def readFile(self,filePath):
        '''Read file (bytes)'''
        with open(filePath,'rb') as f:
            return f.read()
    
    def writeFile(self,filePath,content):
        '''Write to file (bytes)'''
        with open(filePath,'wb') as f:
            f.write(content)

    def generateVaultKey(self):
        '''Create Fernet key and save to default location'''
        print('generating vault.key....')
        key = Fernet.generate_key()
        self.writeFile(self.getRelScriptPath() + '/.hide/vault.key',key)

    def createVaultTable(self):
        '''Create vault with default values at default location'''
        createVaultBool = True      
        if os.path.exists(self.getRelScriptPath() + '/.vault/vault.json'):
            print('!!!! WARNING: a vault already exists at ' + self.getRelScriptPath() + '/.vault/vault.json')
            inputMsg = 'Continue? This will overwrite vault existing at ' 
            inputMsg += self.getRelScriptPath() 
            inputMsg += '/.vault/vault.json [y/n]: '
            option = self.read(inputMsg)
            if option.lower() == 'y':
                if os.path.exists(self.getVaultKeyPath()):
                    os.remove(self.getVaultKeyPath())
                os.remove(self.getRelScriptPath() + '/.vault/vault.json')
            elif option.lower() == 'n':
                createVaultBool = False
                print('Aborting vault creation....\n')
            else:
                createVaultBool = False
                print('No option selected')      
        if createVaultBool is True:
            tmp = { "passwords" : {"tmp":"none"} }
            if not os.path.exists(self.getRelScriptPath() + '/.vault'):
                os.mkdir(self.getRelScriptPath() + '/.vault')            
            self.setVaultKeyPath(self.getRelScriptPath() + '/.hide/vault.key')
            self.setVaultPath(self.getRelScriptPath() + '/.vault/vault.json')
            self.generateVaultKey()
            self.writeFile(self.getVaultPath(),self.encryptByteString(bytes(json.dumps(tmp), 'utf-8')))
            print('\nvault created at ' + self.getRelScriptPath() + '/.vault\n')
 
    def setVaultKeyPath(self,*path):
        '''Set vault key path to object attribute'''
        if not path:
            if self.args.key is not None:
                if os.path.exists(self.args.key):
                    self.vaultKeyPath = self.args.key
                    return
                print('ERROR: Vault key path given as arg != valid path\n')
                return
        elif path:
            if os.path.exists(path[0]):
                self.vaultKeyPath = str(path[0])
                return
        self.vaultKeyPath = self.getRelScriptPath() + '/.hide/vault.key'
    
    def getVaultKeyPath(self):
        return self.vaultKeyPath

    def setVaultPath(self,*path):
        '''Set vault path to object attribute'''
        if not path:
            if self.args.config:
                if os.path.exists(self.args.config):
                    xml = ET.parse(self.args.config)
                    root = xml.getroot()
                    if os.path.exists(root[0].text):
                        self.vaultPath = root[0].text
                        return
                print('ERROR: config path given as arg != valid path\n')
                return
        elif path:
            if os.path.exists(path[0]):
                self.vaultPath = str(path[0])
                return
        self.vaultPath = self.getRelScriptPath() + '/.vault/vault.json'
    
    def getVaultPath(self):
        return self.vaultPath
        
    def getVaultTable(self):
        '''Return JSON of decrypted vault'''
        if os.path.exists(self.getVaultKeyPath()):
            try:
                f = Fernet(self.readFile(self.getVaultKeyPath()))
                decrypted = f.decrypt((self.readFile(self.getVaultPath())))
                return json.loads(decrypted)
            except (IOError, ValueError) as e:
                print(e.errno)
                print(e)
        else:
            print('ERROR: No vault key found at ', self.getVaultKeyPath())
        
    def setRelScriptPath(self):
        self.relScriptPath = os.path.dirname(os.path.abspath(__file__))
        
    def getRelScriptPath(self):
        return self.relScriptPath
        
    def setArgs(self,args):
        self.args = args
        
    def getArgs(self):
        return self.args
    
    def __init__(self,args):
        self.setRelScriptPath()
        self.setArgs(args)
        self.setVaultPath()
        self.setVaultKeyPath()
        