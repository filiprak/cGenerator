'''
Created on 21.03.2017

@author: raqu
'''

from jsonparser.constants import Token

# helper functions
def isWhitespace(character):
    return character == ' ' or character == '\t' or character == '\n' or character == '\r'


class JSONLexer():
    '''
    Loads json file.
    Reads characters from json file and create tokens table
    '''
    def __init__(self):
        self.fileLoaded = False
        
        self.lastChar = None
        self.currentPosition = 0
        self.currentLine = 1
        
        self.bufferSting = None # buffer for file characters
        self.bufferSize = 0
        
    def analyze(self):
        token = Token()
        result = [] # tokenized file contents
        
        currentChar = self.read()
        
        while currentChar:
            if currentChar == '{':
                result.append( (self.currentLine, token.BEGIN_OBJECT.__class__) )
            elif currentChar == '}':
                result.append( (self.currentLine, token.END_OBJECT.__class__) )
            currentChar = self.read()
            
        return result
        
    def read(self, whitespaces=False):
        '''
        Returns next character from buffer, skipping all whitespaces between
        if whitespaces=False, otherwise it reads whitespaces
        '''
        if not self.fileLoaded:
            return None
        
        if self.currentPosition == self.bufferSize:
            return None
        
        self.lastChar = self.bufferSting[self.currentPosition]
        
        # skipping whitespaces
        if not whitespaces:
            while isWhitespace(self.lastChar):
                if self.lastChar == '\n':
                    self.currentLine += 1
                
                self.currentPosition += 1
                if self.currentPosition == self.bufferSize:
                    return None
                
                self.lastChar = self.bufferSting[self.currentPosition]
        
        self.currentPosition += 1
        return self.lastChar
    
    def readString(self):
        return None
    def readNumber(self):
        return None
    def readLiteral(self):
        return None
     
    def loadFile(self, filename):
        '''
        Loads .json file to string format
        :param filename: .json file path
        '''
        try:
            with open(filename) as f:
                self.bufferSting = f.read()
            
        except IOError as ioErr:
            ioErr.args += (filename,)
            raise
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

    