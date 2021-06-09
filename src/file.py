import os

#TO-DO: More error-handling
class file:

    def mkDir(self):
        os.mkdir(os.path.dirname(self.getFilePath))

    def checkParentDir(self):
        return 1 if os.path.exists(self.getParentDir()) else 0

    def getParentDir(self):
        return os.path.dirname(self.getFilePath())

    def rmFile(self):
        if self.checkFile:
            os.remove(self.getFilePath())

    def checkFile(self):
        if os.path.exists(self.getFilePath()):
            return 1
        return 0

    def readFile(self):
        '''Read file (bytes)'''
        if self.checkFile:
            with open(self.getFilePath(),'rb') as f:
                return f.read()
    
    def writeFile(self,content):
        '''Write to file (bytes)'''
        with open(self.getFilePath(),'wb') as f:
            f.write(content)
    
    def setFilePath(self,filePath):
        self.filePath = filePath
        
    def getFilePath(self):
        return self.filePath    
            
    def __init__(self,path):
        self.setFilePath(path)
        