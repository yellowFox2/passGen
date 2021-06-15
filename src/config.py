from .file import file
import xml.etree.ElementTree as ET

class config(file):

    def getRootObj(self):
        return ET.parse(self.getFilePath()).getroot()

    def getVaultPath(self):
        return self.getRootObj()[0].text
        
    def getHashListSize(self):
        return int(self.getRootObj()[1].text)

    def getMethodsKeyIter(self,value):
        '''Retrieve user option elements from XML as dict'''
        options = self.getRootObj().findall("./options/option")
        optionsList = []
        for option in options:
            optionsList.append(option.attrib)
        tmp = {}
        for keyPair in optionsList:
            tmp[keyPair['name']] = keyPair[value]      
        return iter(tmp.items())
    
    def __init__(self,path,defaultPath):
        super(config,self).__init__(path,defaultPath)
