'''
Created on 21.03.2017

@author: raqu
'''

# helper functions
def isWhitespace(character):
    return character == ' ' or character == '\t' or character == '\n' or character == '\r'


class JSONReader():
    '''
    Helps with reading objects from JSON file
    '''
    def __init__(self):
        self.fileLoaded = False
        
        self.lastChar = None
        self.currentPosition = 0
        
        self.bufferSting = None
        self.bufferSize = 0
        
        self.currentLine = 1
      
    def read(self):
        '''
        Returns next character from buffer, skipping all whitespaces between
        '''
        if not self.fileLoaded:
            return None
        
        if self.currentPosition == self.bufferSize:
            return None
        
        self.lastChar = self.bufferSting[self.currentPosition]
        
        # skipping whitespaces
        while isWhitespace(self.lastChar):
            if self.lastChar == '\n':
                self.currentLine += 1
            
            self.currentPosition += 1
            if self.currentPosition == self.bufferSize:
                return None
            
            self.lastChar = self.bufferSting[self.currentPosition]
        
        self.currentPosition += 1
        return self.lastChar
        
    def loadFile(self, filename):
        '''
        Loads .json file to string format
        :param filename: .json file path
        '''
        try:
            with open(filename) as f:
                self.bufferSting = f.read()
            
        except IOError:
            print("Could not read file {}".format(filename))
            return None, 0
        
        if not self.bufferSting or len(self.bufferSting) == 0:
            print("Empty file content: {}".format(filename))
        
        self.bufferSize = len(self.bufferSting)
        
        self.fileLoaded = True
        return self.bufferSting, len(self.bufferSting)
    
    # for testing purposes
    def test(self):
        c = self.read()
        while c:
            print("line-{} char-{}: [{}]".format(self.currentLine, self.currentPosition, c))
            c = self.read()

    
    