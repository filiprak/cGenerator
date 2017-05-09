'''
Created on 07.05.2017

@author: raqu
'''
import re
from generator.ctypes import CVarType, CTypedef, CPreprocConstDefine
from jsonparser.jsonparser import JSONParser
from jsonparser.lexer import JSONLexer
from errors import LexerError, ParserError, LogicError, CSerializeError
from semantic_analyzer.constants import reservedCKeywords


def validCTypename(typename):
    if typename in reservedCKeywords:
        return False
    if ' ' in typename or '\n' in typename or '\r' in typename or '\t' in typename:
        return False
    return re.match("^[_a-zA-Z][_a-zA-Z0-9]*$" , typename) != None
    
def validCidentifier(identifier):
    if identifier in reservedCKeywords:
        return False
    if ' ' in identifier or '\n' in identifier or '\r' in identifier or '\t' in identifier:
        return False
    return re.match("^[_a-zA-Z][_a-zA-Z0-9]*$" , identifier) != None

class Interpreter():
    def __init__(self):
        self.defines = []
        self.declarations = []
        self.definitions = []
        
        self.typesMetadata = dict()
        
        self.currentFile = None
        self.enumerated = None
        
    
    def interpret(self, filesOrder, parsedDict, enumerated):
        self.enumerated = enumerated
        
        for filename in filesOrder:
            self.currentFile = filename
            parsed = parsedDict[filename]
            
            return self.typeINTEGER(parsed)
            
        return self.declarations, self.definitions
    
    
    def typeBOOLEAN(self, jsonobj):
        result = self.typeINTEGER(jsonobj)
        defines = [None, None]
        optional = dict()
        
        if jsonobj.getPair("true-value"):
            if jsonobj.getPair("true-value").holdsString():
                optional[1] = jsonobj.getPairValue("true-value").string
            else:
                raise LogicError(self.currentFile, "Expected valid 'true-value': <string>",
                             line=self.enumerated[jsonobj])
            
        if jsonobj.getPair("false-value"):
            if jsonobj.getPair("false-value").holdsString():
                optional[0] = jsonobj.getPairValue("false-value").string
            else:
                raise LogicError(self.currentFile, "Expected valid 'false-value': <string>",
                             line=self.enumerated[jsonobj])
            
        for boolvalue in optional.keys():
            # check if typename is valid in C
            if not validCTypename(optional[boolvalue]):
                raise LogicError(self.currentFile,
                                 "Type name: '{}' is not valid in C".format(optional[boolvalue]),
                             line=self.enumerated[jsonobj])
            defines[boolvalue] = CPreprocConstDefine(optional[boolvalue], boolvalue)
        return result, defines
    
    
    def typeINTEGER(self, jsonobj):
        typepair = jsonobj.getPair("typeName")
        valid = typepair.holdsString()
        if valid:
            typestring = typepair.value.string
            # check if typename is valid in C
            if not validCTypename(typestring):
                raise LogicError(self.currentFile, "Type name: '{}' is not valid in C".format(typestring),
                             line=self.enumerated[jsonobj])                  
            
            if jsonobj.getPair("min"):
                if jsonobj.getPair("min").holdsNumber():
                    minv = jsonobj.getPairValue("min").value
                    self.typesMetadata[typestring] = { "min":int(minv) }
                else:
                    raise LogicError(self.currentFile, "Expected valid 'min': <integer>",
                                 line=self.enumerated[jsonobj])
            
            if jsonobj.getPair("max"):
                if jsonobj.getPair("max").holdsString():
                    maxv = jsonobj.getPairValue("max").value
                    if not self.typesMetadata[typestring]:
                        self.typesMetadata[typestring] = dict()
                    self.typesMetadata[typestring]["max"] = int(maxv)
                else:
                    raise LogicError(self.currentFile, "Expected valid 'max': <integer>",
                                 line=self.enumerated[jsonobj])
                   
        else:
            raise LogicError(self.currentFile, "Expected valid 'typeName' value: <string>",
                             line=self.enumerated[jsonobj])
        return CTypedef("int", typestring)
    
    
    

"""testing----------------------------------------------------"""
interpr = Interpreter()
lexer = JSONLexer()
parser = JSONParser()
name = "test.json"

try:
    lexer.loadFile(name)
    res = lexer.analyze()
    parsed = parser.parse(res, name)
    
    parsedDict = { name:parsed }
    result = interpr.interpret([name], parsedDict, parser.enumerated)
    
    print(str(result))

    
except IOError as ioErr:
    print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
except LexerError as leErr:
    print(leErr.message)
except ParserError as paErr:
    print(paErr.message)
except LogicError as loErr:
    print(loErr.message)
except CSerializeError as cErr:
    print(cErr.message)
    
    
    
        