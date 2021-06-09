from .file import file

#TO-DO: More error-handling
class config(file):

    def __init__(self,keyPath):
        super().__init__(keyPath)
