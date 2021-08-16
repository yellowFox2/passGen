qfrom .file import file
import xml.etree.ElementTree as ET

#TO-DO: error-handling, remove redundancy
class config(file):
        
    def updateIPFSaddress(self,content):
        self.getRootObj().find('ipfsAddress').text = content
        self.getET().write(self.getFilePath(),encoding='UTF-8',xml_declaration=True)
        self.IPFSaddress = content

    def cast2(self,obj,type):
        if type == 'str':
            return str(obj)
        elif type == 'int':
            return int(obj)
        elif type == 'float':
            return float(obj)
        return None

    def getElem(self,elemName,type):
        try:
            elemVal = self.getRootObj().find(elemName).text.strip()
            return self.cast2(elemVal,type)
        except AttributeError:
            print('\nWARNING: <{0}> elem not set in {1}\n'.format(elemName,self.getFilePath()))
            return None
            
    def getRootObj(self):
        return self.getET().getroot()

    def getMethodsKeyIter(self,value):
        '''Retrieve method aliases from XML as dict'''
        aliases = self.getRootObj().findall("./aliases/alias")
        aliasList = []
        for alias in aliases:
            aliasList.append(alias.attrib)
        tmp = {}
        for keyPair in aliasList:
            tmp[keyPair['name']] = keyPair[value]      
        return iter(tmp.items())
    
    def getIPFSaddress(self):
        return self.IPFSaddress   

    def setIPFSaddress(self):
        self.IPFSaddress = self.getElem('ipfsAddress',str)

    def getET(self):
        return self.ET

    def setET(self):
        self.ET = ET.parse(self.getFilePath())

    def __init__(self,path,defaultPath):
        super(config,self).__init__(path,defaultPath)
        self.setET()
        try:
            self.setIPFSaddress()
        except AttributeError:
            print('\nNo IPFS address set....\n')
