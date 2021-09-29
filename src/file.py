import os

class file(object):
    
    #TO-DO: make shortcut to file
    def mklnk(self,target):
        pass

    def mkDir(self):
        os.mkdir(os.path.dirname(self.getFilePath()))

    def checkParentDir(self):
        return 1 if os.path.exists(self.getParentDir()) else 0

    def getParentDir(self):
        return os.path.dirname(self.getFilePath())

    def rmFile(self):
        if self.checkFile:
            os.remove(self.getFilePath())

    def checkFile(self):
        path = self.getFilePath()
        if path:
            if os.path.exists(self.getFilePath()):
                return True
        return False

    def readFile(self):
        '''Read file (bytes)'''
        if self.checkFile:
            with open(self.getFilePath(),'rb') as f:
                return f.read()
    
    def writeFile(self,content,type):
        '''Write to file (bytes)'''
        with open(self.getFilePath(),type) as f:
            f.write(content)
    
    def setFilePath(self,filePath,defaultPath):
        tmp = filePath
        if tmp:
            self.filePath = tmp if os.path.exists(os.path.dirname(tmp)) else defaultPath
        else:
            self.filePath = defaultPath
        print('\nUsing path: {}\n'.format(self.filePath))
        
    def getFilePath(self):
        return self.filePath    
            
    def __init__(self,path,defaultPath):
        self.setFilePath(path,defaultPath)
        