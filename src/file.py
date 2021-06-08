import os

#TO-DO: More error-handling
class file:

    def readFile(self):
        '''Read file (bytes)'''
        if os.path.exists(self.getFilePath()):
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
        