from .file import file
import xml.etree.ElementTree as ET

class config(file):
 
    def getRootObj(self):
        return ET.parse(self.getFilePath()).getroot()

    def getVaultPath(self):
        return self.getRootObj()[0]

    def getMethods(self):
        '''Retrieve user option elements from XML as dict'''
        options = self.getRootObj().findall("./options/option")
        optionsList = []
        for option in options:
            optionsList.append(option.attrib)
        tmp = {}
        for keyPair in optionsList:
            tmp[keyPair['name']] = keyPair['method']      
        return tmp

    def __init__(self,path,defaultPath):
        super().__init__(path,defaultPath)
