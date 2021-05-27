import os, json
from cryptography.fernet import Fernet
import xml.etree.ElementTree as ET

class vaultTable:
    def updateVaultTable(self,keyName,pw):
        tmp = self.getVaultTable()
        tmp['passwords'][keyName] = pw
        with open(self.vaultKeyPath,'rb') as mykey:
            key = mykey.read()
        f = Fernet(key)
        #TO-DO: error handling -- make sure file is locked
        with open(self.getVaultPath(),'w') as vault:
            json.dump(tmp,vault)
        self.encryptVaultTable()

    def getVaultTable(self):
        with open(self.vaultKeyPath,'rb') as mykey:
            key = mykey.read()
        f = Fernet(key)
        with open(self.getVaultPath(),'rb') as encryptedVault:
            encrypted = encryptedVault.read()
        decrypted = f.decrypt(encrypted)
        return json.loads(decrypted)

    def getVaultPath(self):
        if self.args.config:
            if os.path.exists(args.config):
                xml = ET.parse(args.config)
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
        with open(self.vaultKeyPath,'rb') as mykey:
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
        with open(self.vaultKeyPath, 'wb') as mykey:
            mykey.write(key)

    def createVaultTable(self):
        tmp = { "passwords" : {"tmp":"none"} }
        if not os.path.exists(self.getRelScriptPath() + '\.vault'):
            os.mkdir(self.getRelScriptPath() + '\.vault')
        with open(self.getRelScriptPath() + '\.vault\\vault.json','w+') as f:
            json.dump(tmp,f)
        f.close()
        print('vault created at .\.vault\n')
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
    