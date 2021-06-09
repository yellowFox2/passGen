import os
import xml.etree.ElementTree as ET
from .file import file

class vaultTable(file):
      
    def setVaultPath(self,defaultPath):
        '''Set vault path to object attribute'''
        config = self.getConfig()
        try:
            if self.checkFile(config.getVaultPath()):
                vaultPath = config.getVaultPath()
                if vaultPath:
                    if os.path.exists(vaultPath):
                        super().__init__(vaultPath,defaultPath)
        except:
            super().__init__(None,defaultPath)

    def setConfig(self,configObj):
        self.config = configObj

    def getConfig(self):
        return self.config
    
    #TO-DO: only pass file path -- check for config in main and if given path in config exists
    def __init__(self,configObj,defaultPath):
        self.setConfig(configObj)
        self.setVaultPath(defaultPath)
        