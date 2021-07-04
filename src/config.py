from .file import file
import xml.etree.ElementTree as ET

#TO-DO: error-handling, remove redundancy
class config(file):

    def setET(self):
        self.ET = ET.parse(self.getFilePath())

    def getET(self):
        return self.ET

    def getRootObj(self):
        return self.getET().getroot()

    def getVaultPath(self):
        return self.getRootObj().find('vaultPath').text
        
    def getHashListSize(self):
        return int(self.getRootObj().find('hashListSize').text)
    
    def getSpecCharChance(self):
        return float(self.getRootObj().find('specCharChance').text)

    def updateIPFSaddress(self,content):
        self.getRootObj().find('ipfsAddress').text = content
        self.getET().write(self.getFilePath(),encoding='UTF-8',xml_declaration=True)
        self.IPFSaddress = content

    def setIPFSaddress(self):
        self.IPFSaddress = str(self.getRootObj().find('ipfsAddress').text).strip()

    def getIPFSaddress(self):
        return self.IPFSaddress

    def getMethodsKeyIter(self,value):
        '''Retrieve user option elements from XML as dict'''
        aliases = self.getRootObj().findall("./aliases/alias")
        aliasList = []
        for alias in aliases:
            aliasList.append(alias.attrib)
        tmp = {}
        for keyPair in aliasList:
            tmp[keyPair['name']] = keyPair[value]      
        return iter(tmp.items())
    
    def __init__(self,path,defaultPath):
        super(config,self).__init__(path,defaultPath)
        self.setET()
        try:
            self.setIPFSaddress()
        except AttributeError:
            print('\nNo IPFS address set....\n')
