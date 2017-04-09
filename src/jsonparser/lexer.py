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
                number = self.readNumber()
                result.append( (self.currentLine, Token.NUMBER, number) )
            elif currentChar == '-':
                number = self.readNumber()
                result.append( (self.currentLine, Token.NUMBER, number) )   
            elif currentChar == '"':
                string = self.readString()
                result.append( (self.currentLine, Token.STRING, string) ) 
            else:
                raise LexerError(self.errorMessage(token=self.lastChar),
                                 self.getFileLine(self.currentLine) )
                
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
        
        if character != '"':
            raise LexerError(self.errorMessage(expected=" '\"' at the end of STRING token"),
                                 self.getFileLine(self.currentLine) )
        
        return string
    
    
    def readNumber(self):
        '''
        Reads integer or float number, supports exponent notation
        Puts read number into a string
        '''
        number = self.readInteger()
        
        if self.nextChar == '.':
            self.read(whitespaces=True)
            number += '.'
            number += self.readFraction()
            if self.nextChar == 'E' or self.nextChar == 'e':    
                self.read(whitespaces=True)
                number += self.lastChar
                number += self.readExponent()
            return number
        
        elif self.nextChar == 'E' or self.nextChar == 'e':    
            self.read(whitespaces=True)
            number += self.lastChar
            number += self.readExponent()
           
        return number
    
    def readExponent(self):
        '''
        Reads exponent part of number
        '''
        exponent = ""
        self.read(whitespaces=True)
        
        if isDigit(self.lastChar):
            exponent += self.lastChar
            while isDigit(self.nextChar):
                self.read(whitespaces=True)
                exponent += self.lastChar
            return exponent
        
        elif self.lastChar == '-' or self.lastChar == '+':
            exponent += self.lastChar
            self.read(whitespaces=True)
            if isDigit(self.lastChar):
                exponent += self.lastChar
                while isDigit(self.nextChar):
                    self.read(whitespaces=True)
                    exponent += self.lastChar
                return exponent
            else:
                raise LexerError(self.errorMessage(token="bad exponent format"),
                                 self.getFileLine(self.currentLine) )
                
        else:
            raise LexerError(self.errorMessage(token="bad exponent format"),
                                 self.getFileLine(self.currentLine) )
        
        return exponent
            
    def readInteger(self):
        '''
        Reads integer and puts it into string
        '''
        integer = ""
        if self.lastChar == '-':
            integer += '-'
            self.read(whitespaces=True)
        
        if not isDigit(self.lastChar):
            raise LexerError(self.errorMessage(token="bad number format"),
                                 self.getFileLine(self.currentLine) )
        if not isDigit(self.nextChar):
            return integer + self.lastChar
        
        if self.lastChar == '0':
            raise LexerError(self.errorMessage(token="bad zero format"),
                                 self.getFileLine(self.currentLine) )
        
        integer += self.lastChar
        
        while isDigit(self.nextChar):
            self.read(whitespaces=True)
            integer += self.lastChar
        return integer
    
    def readFraction(self):
        fraction = ""
        self.read(whitespaces=True)
        
        if isDigit(self.lastChar):
            fraction += self.lastChar
            while isDigit(self.nextChar):
                self.read(whitespaces=True)
                fraction += self.lastChar
            return fraction
        else:
            raise LexerError(self.errorMessage(token="bad fraction part format"),
                                 self.getFileLine(self.currentLine) )
        return fraction
    
    def readLiteral(self):
        '''
        Reads literal
        '''
        nullLiteral = ['u', 'l', 'l']
        trueLiteral = ['r', 'u', 'e']
        falseLiteral = ['a', 'l', 's', 'e']
        
        if self.lastChar == 'n':
            for charact in nullLiteral:
                self.read()
                if charact != self.lastChar:
                    raise LexerError(self.errorMessage(expected="null"),
                                 self.getFileLine(self.currentLine) )
                
            return "null"
                
        elif self.lastChar == 't':
            for charact in trueLiteral:
                self.read()
                if charact != self.lastChar:
                    raise LexerError(self.errorMessage(expected="true"),
                                 self.getFileLine(self.currentLine) )
                
            return "true"
                
        elif self.lastChar == 'f':
            for charact in falseLiteral:
                self.read()
                if charact != self.lastChar:
                    raise LexerError(self.errorMessage(expected="false"),
                                 self.getFileLine(self.currentLine) )
                
            return "false"
                
        else:
            raise LexerError(line=self.getFileLine(self.currentLine) )
        
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
        
    def getFileLine(self, lineNr):
        '''
        Returns character string of line of given number
        :param lineNr: number of line to get
        '''
        if lineNr == None:
            return "empty line"
        linenum = 1
        strline = ""
        for character in self.bufferSting:
            strline += character 
            if character == '\n':
                if linenum == lineNr:
                    return strline
                linenum += 1
                strline = ""    
                
        return "EOF"
    
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
    
    