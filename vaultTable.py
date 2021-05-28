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
        if os.path.exists(self.getVaultKeyPath()):
            with open(self.getVaultKeyPath(),'rb') as mykey:
                key = mykey.read()
            f = Fernet(key)
            with open(self.getVaultPath(),'rb') as encryptedVault:
                encrypted = encryptedVault.read()
            decrypted = f.decrypt(encrypted)
            try:
                print(json.dumps(json.loads(decrypted),sort_keys=True,indent=4))
            except:
                print(json.loads(decrypted))
        else:
            print('ERROR: No vault key found at ', self.getVaultKeyPath())
            
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

    def getVaultPath(self):
        if self.args.config:
            if os.path.exists(self.args.config):
                xml = ET.parse(self.args.config)
            else:
                xmlPath = self.getRelScriptPath() + '\config\\config.xml'
                xml = ET.parse(xmlPath)
        else:
            xmlPath = self.getRelScriptPath() + '\config\\config.xml'
            xml = ET.parse(xmlPath)
        root = xml.getroot()
        if root[0].text == None:
            return self.getRelScriptPath() + '\.vault\\vault.json'
        return root[0].text

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
        with open(self.getVaultKeyPath(), 'wb') as mykey:
            mykey.write(key)

    def createVaultTable(self):
        createVaultBool = True      
        if os.path.exists(self.getRelScriptPath() + '\.vault\\vault.json'):
            print('!!!! WARNING: a vault already exists at ' + self.getRelScriptPath() + '\\.vault\\vault.json')
            inputMsg = 'Continue? This will overwrite vault existing at ' + self.getRelScriptPath() + '\\.vault\\vault.json [y/n]: '
            option = self.read(inputMsg)
            if option.lower() == 'y':
                if os.path.exists(self.getVaultKeyPath()):
                    os.remove(self.getVaultKeyPath())
                os.remove(self.getRelScriptPath() + '\.vault\\vault.json')
            elif option.lower() == 'n':
                createVaultBool = False
                print('Aborting vault creation....\n')
            else:
                createVaultBool = False
                print('No option selected')      
        if createVaultBool == True:
            tmp = { "passwords" : {"tmp":"none"} }
            if not os.path.exists(self.getRelScriptPath() + '\.vault'):
                os.mkdir(self.getRelScriptPath() + '\.vault')
            with open(self.getRelScriptPath() + '\.vault\\vault.json','w+') as f:
                json.dump(tmp,f)
            f.close()
            print('vault created at ' + self.getRelScriptPath() + '\.vault\n')
            self.setVaultKeyPath(self.getArgs())
            self.generateVaultKey()
            self.encryptVaultTable()
    
    def setVaultKeyPath(self,args):
        if args.key == None:
            self.vaultKeyPath = self.getRelScriptPath() + '\.hide\\vault.key'
        elif os.path.exists(args.key):
            self.vaultKeyPath = args.key
        else:
            print('invalid path')
            self.vaultKeyPath = self.getRelScriptPath() + '\.hide\\vault.key'
    
    def getVaultKeyPath(self):
        return self.vaultKeyPath
    
    def setRelScriptPath(self):
        self.relScriptPath = os.path.dirname(os.path.abspath(__file__))
        
    def getRelScriptPath(self):
        return self.relScriptPath
    
    def getVaultKeyPath(self):
        return self.vaultKeyPath
        
    def setArgs(self,args):
        self.args = args
        
    def getArgs(self):
        return self.args
    
    def __init__(self,args):
        self.setRelScriptPath()
        self.setArgs(args)
        self.setVaultKeyPath(self.getArgs())