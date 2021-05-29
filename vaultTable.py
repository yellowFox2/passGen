import os, json, sys
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ET

class vaultTable:
    def read(self,prompt):
        if sys.version_info[0] == 2:
            return raw_input(prompt)
        else:
            return input(prompt)
            
    def updateVaultTable(self):
        if not os.path.exists(self.getVaultKeyPath()):
            print('ERROR: No vault key found at ', self.getVaultKeyPath())
        else:
            siteAlias = self.read('site alias? (i.e. "reddit")\n')
            tmp = self.getVaultTable()
            pw = self.read('enter pw:\n')
            tmp['passwords'][siteAlias] = pw
            with open(self.getVaultKeyPath(),'rb') as mykey:
                key = mykey.read()
            f = Fernet(key)
            #TO-DO: error handling -- make sure file is locked
            with open(self.getVaultPath(),'w') as vault:
                json.dump(tmp,vault)
            self.encryptVaultTable()

    def printVaultTable(self):
            if self.getVaultTable():
                try:
                    print(json.dumps(self.getVaultTable(),sort_keys=True,indent=4))
                except:
                    print(self.getVaultTable())
            
    def encryptVaultTable(self):
        with open(self.getVaultKeyPath(),'rb') as mykey:
            key = mykey.read()
        f = Fernet(key)
        vaultPath = self.getVaultPath()
        with open(vaultPath,'rb') as unencryptedVault:
            unencrypted = unencryptedVault.read()
        encrypted = f.encrypt(unencrypted)
        with open(vaultPath,'wb') as encryptedVault:
            encryptedVault.write(encrypted)

    def generateVaultKey(self):
        print('generating vault.key....')
        key = Fernet.generate_key()
        with open(self.getRelScriptPath() + '/.hide/vault.key', 'wb') as mykey:
            mykey.write(key)

    def createVaultTable(self):
        createVaultBool = True      
        if os.path.exists(self.getRelScriptPath() + '/.vault/vault.json'):
            print('!!!! WARNING: a vault already exists at ' + self.getRelScriptPath() + '/.vault/vault.json')
            inputMsg = 'Continue? This will overwrite vault existing at ' + self.getRelScriptPath() + '/.vault/vault.json [y/n]: '
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
        if createVaultBool == True:
            tmp = { "passwords" : {"tmp":"none"} }
            if not os.path.exists(self.getRelScriptPath() + '/.vault'):
                os.mkdir(self.getRelScriptPath() + '/.vault')
            with open(self.getRelScriptPath() + '/.vault/vault.json','w+') as f:
                json.dump(tmp,f)
            f.close()
            print('vault created at ' + self.getRelScriptPath() + '/.vault\n')
            self.setVaultKeyPath(self.getRelScriptPath() + '/.hide/vault.key')
            self.setVaultPath(self.getRelScriptPath() + '/.vault/vault.json')
            self.generateVaultKey()
            self.encryptVaultTable()
    
    def setVaultKeyPath(self,*path):
        if not path:
            if self.args.key != None:
                if os.path.exists(self.args.key):
                    self.vaultKeyPath = self.args.key
                    return
                else:
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
        if not path:
            if self.args.config:
                if os.path.exists(self.args.config):
                    xml = ET.parse(self.args.config)
                    root = xml.getroot()
                    if os.path.exists(root[0].text):
                        self.vaultPath = root[0].text
                        return
                    else:
                        print('ERROR: Vault path given in config != valid path\n')
                        return
                else:
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
        if os.path.exists(self.getVaultKeyPath()):
            with open(self.getVaultKeyPath(),'rb') as mykey:
                key = mykey.read()
            f = Fernet(key)
            with open(self.getVaultPath(),'rb') as encryptedVault:
                encrypted = encryptedVault.read()
            decrypted = f.decrypt(encrypted)
            return json.loads(decrypted)
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