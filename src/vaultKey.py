from cryptography.fernet import Fernet
from .file import file

class vaultKey(file):

    def generateVaultKey(self):
        '''Create Fernet key and save to default location'''
        print('generating vault.key....')
        key = Fernet.generate_key()
        self.writeFile(key)

    def __init__(self,keyPath):
        super().__init__(keyPath)
