'''
Created on 21.03.2017
Lexer module: reads characters from file and
recognizes tokens, outputs token table
@author: raqu
'''

from .constants import Token
from errors import LexerError


""" helper functions """
def isWhitespace(character):
    if not character:
        return False
    
    return character == ' ' or character == '\t' or character == '\n' or character == '\r'

def isDigit(character, isNonzero=False):
    if not character:
        return False
    
    if isNonzero and character == '0':
        return False
    
    return character == '0' or character == '1' \
            or character == '2' or character == '3' \
            or character == '4' or character == '5' \
            or character == '6' or character == '7' \
            or character == '8' or character == '9'


class JSONLexer():
    '''
    Loads json file.
    Reads characters from json file and create tokens table
    '''
    def __init__(self):
        self.fileLoaded = False
        self.currentFile = None # currently processed file name
        
        self.lastChar = None # last read character
        self.nextChar = None # next character to be read
        self.currentPosition = 0 # number of chars from the file begining
        self.currentLine = 1 # currently processed file line
        
        self.bufferSting = None # buffer for file characters
        self.bufferSize = 0 # number of chars in the file
        
    def analyze(self):
        '''
        Recognizes tokens and puts it into result list
        '''
        result = [] # tokenized file contents
        
        currentChar = self.read()
        
        while currentChar:
            if currentChar == '{':
                result.append( (self.currentLine, Token.BEGIN_OBJECT, "{") )
            elif currentChar == '}':
                result.append( (self.currentLine, Token.END_OBJECT, "}") )
            elif currentChar == '[':
                result.append( (self.currentLine, Token.BEGIN_ARRAY, "[") )
            elif currentChar == ']':
                result.append( (self.currentLine, Token.END_ARRAY, "]") )
            elif currentChar == ':':
                result.append( (self.currentLine, Token.COLON, ":") )
            elif currentChar == ',':
                result.append( (self.currentLine, Token.COMA, ",") )
            elif currentChar == 'n' or currentChar == 't' or currentChar == 'f':
                literal = self.readLiteral()
                result.append( (self.currentLine, Token.LITERAL, literal) )
            elif isDigit(currentChar):
                number = self.readInteger()
                result.append( (self.currentLine, Token.NUMBER, number) )
            elif currentChar == '-':
                number = self.readInteger()
                result.append( (self.currentLine, Token.NUMBER, number) )   
            elif currentChar == '"':
                string = self.readString()
                result.append( (self.currentLine, Token.STRING, string) ) 
            else:
                raise LexerError(self.errorMessage(token=self.lastChar))
                
            currentChar = self.read()
            
        return result


    def read(self, whitespaces=False):
        '''
        Returns next character from buffer, skipping all whitespaces between
        if whitespaces=False, otherwise it reads whitespaces
        Sets current character and next character properly
        '''
        if not self.fileLoaded:
            return None
        
        if self.currentPosition == self.bufferSize:
            return None
        
        self.lastChar = self.bufferSting[self.currentPosition]
        
        # skipping whitespaces for lastChar
        if not whitespaces:
            while isWhitespace(self.lastChar):
                if self.lastChar == '\n':
                    self.currentLine += 1
                
                self.currentPosition += 1
                if self.currentPosition == self.bufferSize:
                    return None
                
                self.lastChar = self.bufferSting[self.currentPosition]

        # looking for next character
        if self.currentPosition + 1 == self.bufferSize:
            self.nextChar = None
        elif not whitespaces:
            # skipping whitespaces
            i = self.currentPosition + 1
            self.nextChar = self.bufferSting[i]
            while isWhitespace(self.nextChar):
                i += 1
                if i == self.bufferSize:
                    self.nextChar = None
                    break
                self.nextChar = self.bufferSting[i]
        else:
            self.nextChar = self.bufferSting[self.currentPosition + 1]

        self.currentPosition += 1
        return self.lastChar
    
    
    def readString(self):
        '''
        Reads string of characters
        '''
        string = ""
        character = self.read(whitespaces=True)
        while character and character != '"':
            string += character
            character = self.read(whitespaces=True)
            
        return string
    
    
    """def readNumber(self):
       
        if self.lastChar == '0':
            if self.nextChar != '.':
                number += "0."
                while isDigit(self.read()):
                    number += self.lastChar
                    
                
            else:
                return "0"
        else:
            raise
        while self.lastChar:
            
            self.read()
            
        return number"""
    
    def readInteger(self):
        '''
        Reads integer to string
        '''
        integer = ""
        if self.lastChar == '-':
            integer += '-'
            self.read()
        
        if not isDigit(self.lastChar):
            raise LexerError(self.errorMessage(token="bad number format"))
        if not isDigit(self.nextChar):
            return integer + self.lastChar
        
        integer += self.lastChar
        while isDigit(self.nextChar):
            self.read()
            integer += self.lastChar
        return integer
        
    
    def readLiteral(self):
        '''
        Reads literal
        '''
        nullLiteral = ['n', 'u', 'l', 'l']
        trueLiteral = ['t', 'r', 'u', 'e']
        falseLiteral = ['f', 'a', 'l', 's', 'e']
        
        if self.lastChar == 'n':
            for charact in nullLiteral:
                if charact != self.lastChar:
                    raise LexerError(self.errorMessage(expected="null"))
                self.read()
            return "null"
                
        elif self.lastChar == 't':
            for charact in trueLiteral:
                if charact != self.lastChar:
                    raise LexerError(self.errorMessage(expected="true"))
                self.read()
            return "true"
                
        elif self.lastChar == 'f':
            for charact in falseLiteral:
                if charact != self.lastChar:
                    raise LexerError(self.errorMessage(expected="false"))
                self.read()
            return "false"
                
        else:
            raise LexerError()
        
        return None
    
    
    def errorMessage(self, expected=None, token=None):
        '''
        Creates error message from parameters:
        :param expected: expected value/token
        :param token: points where has occured an error (file fragment)
        '''
        message = "Unrecognized token"
        if token:
            message += ": " + str(token)
        if expected:
            message += ", expected: " + str(expected)
        return str(self.currentFile) + ": line: " + str(self.currentLine) + ": " + message 
        
    
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
        self.currentFile = filename
        return self.bufferSting, len(self.bufferSting)
    
    