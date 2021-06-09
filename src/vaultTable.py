import os
import xml.etree.ElementTree as ET
from .file import file

class vaultTable(file):
    
    #TO-DO: Remove need for passing config obj + move most logic to main      
    def setVaultPath(self):
        '''Set vault path to object attribute'''
        if self.getConfig().checkFile():
            xml = ET.parse(self.getConfig().getFilePath())
            root = xml.getroot()
            if root[0].text:
                if os.path.exists(root[0].text):
                    super().__init__(root[0].text)
                    return
        xml = ET.parse(self.getConfig().getFilePath())
        root = xml.getroot()
        if root[0].text:
            if os.path.exists(root[0].text):
                super().__init__(root[0].text)
                return
        confParentDir = file(self.getConfig().getParentDir())
        confGParentDir = file(confParentDir.getParentDir())
        super().__init__(confGParentDir.getFilePath() + '/.vault/vault.json')

    def setConfig(self,configObj):
        self.config = configObj

    def getConfig(self):
        return self.config
    
    #TO-DO: only pass file path -- check for config in main and if given path in config exists
    def __init__(self,configObj):
        self.setConfig(configObj)
        self.setVaultPath()
        