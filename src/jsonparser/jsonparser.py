'''
Created on 21.03.2017
JSON parser module
@author: raqu
'''

from .constants import Token
from errors import ParserError
from .jsontypes import JSONObject, JSONPair, JSONString, JSONNumber,\
    JSONLiteral, JSONArray


class JSONParser():
    '''
    Main JSON jsonparser class
    '''
    def __init__(self):
        self.currentFile = None
        self.tokenized = None
        self.currToken = None
        self.tokenizedSize = 0
        self.currentPosition = -1
        
        
    def nextToken(self):
        '''
        Reads next token from tokenized file, and return its code (Token.*)
        '''
        if self.currentPosition >= self.tokenizedSize:
            return None
        self.currentPosition += 1
        (line, token, string) = self.tokenized[self.currentPosition]
        self.currToken = token
        return token
    
    
    def tokenInfo(self):
        '''
        Returns line number, token code and token string value of current token.
        '''
        if self.currentPosition < 0:
            return None, None, None
        (line, token, string) = self.tokenized[self.currentPosition]
        return line, token, string
        
    
    def parse(self, tokenized, filename):
        '''
        Parses tokenized json to object tree
        :param tokenized: token list of tuples (lineNr, tokenType, value)
        :param filename: name of parsed file
        '''
        if tokenized == None:
            return None
        self.currentFile = filename
        self.tokenized = tokenized
        self.tokenizedSize = len(tokenized)
        self.currToken = None
        self.currentPosition = -1
        
        if self.nextToken() != Token.BEGIN_OBJECT:
            line, token, string = self.tokenInfo()
            raise ParserError(self.errorMessage(expected="{", token=string), line)
        
        return self.parseJSONObject()
    
    
    def parseJSONObject(self):
        '''
        Parses json object, returns JSONObject
        '''
        jsonobject = JSONObject()
        
        self.nextToken()
        if self.currToken == Token.END_OBJECT:
            return jsonobject
            
        pair = self.parseJSONPair()
        jsonobject.append(pair)
        
        while self.nextToken() != None:
            if self.currToken == Token.END_OBJECT:
                return jsonobject
            if self.currToken != Token.COMA:
                line, token, string = self.tokenInfo()
                raise ParserError(self.errorMessage(token=string,
                                    expected=" ',' separator" ),line)
            self.nextToken()
            pair = self.parseJSONPair()
            jsonobject.append(pair)
        
        line, token, string = self.tokenInfo()
        raise ParserError(self.errorMessage(expected=" '}' at the end of JSON object"), line)
    
    
    def parseJSONArray(self):
        '''
        Parses json array, returns JSONArray object
        '''
        jsonarray = JSONArray()
        
        while self.nextToken() != None:
            if self.currToken == Token.END_ARRAY:
                return jsonarray
            
            if not jsonarray.empty():
                if self.currToken != Token.COMA:
                    line, token, string = self.tokenInfo()
                    raise ParserError(self.errorMessage(token=string,
                                        expected=" ',' separator" ),line)
                self.nextToken()
                
            if self.currToken == Token.BEGIN_OBJECT:
                element = self.parseJSONObject()
            elif self.currToken == Token.BEGIN_ARRAY:
                element = self.parseJSONArray()
            elif self.currToken == Token.STRING:
                element = self.parseJSONString()
            elif self.currToken == Token.NUMBER:
                element = self.parseJSONNumber()
            elif self.currToken == Token.LITERAL:
                element = self.parseJSONLiteral()
            else:
                line, token, string = self.tokenInfo()
                raise ParserError(self.errorMessage(token=string,
                                 expected="correct array element"), line)
            jsonarray.insert(element)
        
        line, token, string = self.tokenInfo()
        raise ParserError(self.errorMessage(expected=" ']' at the end of JSON array"), line)
    
    
    def parseJSONString(self):
        '''
        Parses json string, returns JSONString object.
        '''
        line, token, string = self.tokenInfo()
        if self.currToken != Token.STRING:
            raise ParserError(self.errorMessage(token=string, expected="quoted string value"), line)
        
        return JSONString(string)
    
    
    def parseJSONNumber(self):
        '''
        Parses json number, returns JSONNumber object.
        '''
        line, token, string = self.tokenInfo()
        if self.currToken != Token.NUMBER:
            raise ParserError(self.errorMessage(token=string, expected="number value"), line)
        
        return JSONNumber(string)


    def parseJSONPair(self):
        '''
        Parses one json pair, returns JSONPair object.
        '''
        line, token, string = self.tokenInfo()
        if self.currToken != Token.STRING:
            raise ParserError(self.errorMessage(expected=" value name, format: <name>:<value>"), line)
        name = string
        if self.nextToken() != Token.COLON:
            line, token, string = self.tokenInfo()
            raise ParserError(self.errorMessage(expected=" ':', format: <name>:<value>"), line)
        self.nextToken()
        if self.currToken == Token.BEGIN_OBJECT:
            value = self.parseJSONObject()
        elif self.currToken == Token.BEGIN_ARRAY:
            value = self.parseJSONArray()
        elif self.currToken == Token.STRING:
            value = self.parseJSONString()
        elif self.currToken == Token.NUMBER:
            value = self.parseJSONNumber()
        elif self.currToken == Token.LITERAL:
            value = self.parseJSONLiteral()
        else:
            line, token, string = self.tokenInfo()
            raise ParserError(self.errorMessage(token=string,
                             expected="correct \"" + name + "\" value"), line)
        
        return JSONPair(name, value)
    
    
    def parseJSONLiteral(self):
        '''
        Parses json literal: null, true, false, returns proper JSONLiteral object.
        '''
        line, token, string = self.tokenInfo()
        if self.currToken != Token.LITERAL:
            raise ParserError(self.errorMessage(token=string, expected="one of: null | false | true"), line)
        
        return JSONLiteral(string)
    
    
    def errorMessage(self, expected=None, token=None):
        '''
        Creates error message from parameters:
        :param expected: expected value/token
        :param token: points where has occured an error (file fragment)
        '''
        message = "Unexpected token"
        if token:
            message += ": " + token
        if expected:
            message += " -expected: " + str(expected)
            
        line, t, s = self.tokenInfo()
        return str(self.currentFile) + ": line: " + str(line) + ": " + message 
    
    