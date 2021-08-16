from .file import file
import os

class bash(file):

    def createShortcut(self,shortcutPath):
        if os.path.exists(os.path.dirname(shortcutPath)):
            os.system('ln -s {0} {1}'.format(self.getFilePath(),shortcutPath))
            os.system('chmod +x {0}'.format(shortcutPath))
        else:
            print('\nERROR: Invalid shortcut path: {}\n'.format(shortcutPath))

    def setFilePath(self,scriptPath,defaultPath):
        self.filePath = scriptPath if os.path.exists(os.path.dirname(scriptPath)) else defaultPath
        print('\nUsing path: {}\n'.format(self.filePath))

    def __init__(self,scriptPath,defaultPath):
        super(bash,self).__init__(scriptPath,defaultPath)