import os
import xml.etree.ElementTree as ET
from .file import file

class vaultTable(file):
          
    def setVaultPath(self):
        '''Set vault path to object attribute'''
        if self.args:
            if self.args.config:
                if os.path.exists(self.args.config):
                    xml = ET.parse(self.args.config)
                    root = xml.getroot()
                    if os.path.exists(root[0].text):
                        super().__init__(root[0].text)
                        return
        xml = ET.parse(self.getRelScriptPath() + '/config/config.xml')
        root = xml.getroot()
        if root[0].text:
            if os.path.exists(root[0].text):
                super().__init__(root[0].text)
                return
        super().__init__(self.getRelScriptPath() + '/.vault/vault.json')
    
    #TO-DO: Remove need to pass script path to instance
    def setRelScriptPath(self,path):
        self.relScriptPath = path
        
    def getRelScriptPath(self):
        return self.relScriptPath
    
    #TO-DO: Remove need to pass arguments to instance
    def setArgs(self,args):
        self.args = args
        
    def getArgs(self):
        return self.args
    
    def __init__(self,args,scriptPath):
        self.setRelScriptPath(scriptPath)
        self.setArgs(args)
        self.setVaultPath()
        