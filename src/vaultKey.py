from cryptography.fernet import Fernet
from .file import file

#TO-DO: More error-handling
class vaultKey(file):

    def encryptByteString(self,inputString):
        '''Encrypt a bytes object -- convert a string to bytes first -- using vault key'''
        f = Fernet(self.readFile())
        return f.encrypt(inputString)
        
    def decryptByteString(self,inputString):
        '''Decrypt a bytes object using vault key'''
        tmp = self.readFile()
        if tmp:
            f = Fernet(tmp)
            return f.decrypt(inputString)       

    def generateVaultKey(self):
        '''Create Fernet key and save to default location'''
        print('generating vault.key....')
        key = Fernet.generate_key()
        self.writeFile(key,'wb')

    def __init__(self,keyPath,defaultPath):
        super(vaultKey,self).__init__(keyPath,defaultPath)
