import os
from .file import file

class vaultTable(file):
    
    # def setFilePath(self,configuredPath,defaultPath):
        # tmp = configuredPath
        # if tmp:
            # self.filePath = tmp if os.path.exists(os.path.dirname(tmp)) else defaultPath
        # else:
            # self.filePath = defaultPath
        # print('\nUsing path: {}\n'.format(self.filePath))

    def setEncryptedVaultTable(self,content):
        self.encryptedVaultTable = bytes(content)

    def getEncryptedVaultTable(self):
        return self.encryptedVaultTable

    def __init__(self,configuredPath,defaultPath):
        super(vaultTable,self).__init__(configuredPath,defaultPath)
        