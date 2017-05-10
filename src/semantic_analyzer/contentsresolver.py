'''
Created on 07.05.2017

@author: raqu
'''
import re
from generator.ctypes import CVarType, CTypedef, CPreprocConstDefine, CArrayType,\
    CStructType, CEnumType
from jsonparser.jsonparser import JSONParser
from jsonparser.lexer import JSONLexer
from errors import LexerError, ParserError, LogicError, CSerializeError
from semantic_analyzer.constants import reservedCKeywords, asn1types

# helper functions
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
            
            self.declarations.append(self.typeSEQUENCE(parsed))
            
        return self.declarations, self.definitions
    
    
    def typeBOOLEAN(self, jsonobj):
        result = self.typeINTEGER(jsonobj)
        defines = [None, None]
        optional = dict()
        
        if jsonobj.getPair("true-value"):
            if jsonobj.getPair("true-value").holdsString():
                optional[1] = jsonobj.getPairValue("true-value").string
            else:
                raise self.ContextLogicError("Expected valid 'true-value': <string>", jsonobj)
            
        if jsonobj.getPair("false-value"):
            if jsonobj.getPair("false-value").holdsString():
                optional[0] = jsonobj.getPairValue("false-value").string
            else:
                raise self.ContextLogicError("Expected valid 'false-value': <string>", jsonobj)
            
        for boolvalue in optional.keys():
            # check if typename is valid in C
            if not validCTypename(optional[boolvalue]):
                raise self.ContextLogicError("Type name: '{}' is not valid in C".format(optional[boolvalue]), jsonobj)
            defines[boolvalue] = CPreprocConstDefine(optional[boolvalue], boolvalue)
        return result, defines
    
    
    def typeINTEGER(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)                
        if jsonobj.getPair("min"):
            val = self.validConstraintPair(jsonobj, "min")
            self.addTypeMetadata(typestring, "min", int(val))
        
        if jsonobj.getPair("max"):
            val = self.validConstraintPair(jsonobj, "max")
            self.addTypeMetadata(typestring, "max", int(val))
            
            if "min" in self.typesMetadata[typestring]:
                if self.typesMetadata[typestring]["min"] > int(val):
                    raise self.ContextLogicError("Bad INTEGER constraints: min > max", jsonobj)
        
        ctype = "int"
        if jsonobj.getPair("encoding"):
            encoding = self.validEncodingPair(jsonobj)
            if encoding == "pos-int":
                ctype = "unsigned"
            elif encoding == "twos-complement":
                ctype = "int"
            else:
                raise self.ContextLogicError("Illegal encoding property for INTEGER type", jsonobj)
            
            self.addTypeMetadata(typestring, "encoding", encoding)
        
        return CTypedef(ctype, typestring)
    
    def typeBIT_STRING(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        if not jsonobj.getPair("size"):
            raise self.ContextLogicError("Size constraint must be specified for BIT STRING: 'size':<integer>", jsonobj)
        size = self.validConstraintPair(jsonobj, "size")
        nrints = int(size / 32) + 1
        bitarrayt = CArrayType("int", "bitarray", nrints)
        structt = CStructType(typestring, [bitarrayt])
        typedef = CTypedef(structt, typestring)
        return typedef
    
    def typeCHARACTER_STRING(self, jsonobj):
        return self.typeOCTET_STRING(jsonobj)
    
    def typeOCTET_STRING(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        if not jsonobj.getPair("size"):
            raise self.ContextLogicError("Size constraint must be specified for CHAR/OCTET STRING: 'size':<integer>", jsonobj)
        size = self.validConstraintPair(jsonobj, "size")
        chararrayt = CArrayType("char", "bytes", int(size))
        structt = CStructType(typestring, [chararrayt])
        typedef = CTypedef(structt, typestring)
        return typedef
    
    def typeREAL(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)                
        if jsonobj.getPair("min"):
            val = self.validConstraintPair(jsonobj, "min")
            self.addTypeMetadata(typestring, "min", float(val))
        
        if jsonobj.getPair("max"):
            val = self.validConstraintPair(jsonobj, "max")
            self.addTypeMetadata(typestring, "max", float(val))
            
            if "min" in self.typesMetadata[typestring]:
                if self.typesMetadata[typestring]["min"] > float(val):
                    raise self.ContextLogicError("Bad FLOAT constraints: min > max", jsonobj)
                
        ctype = "double"
        if jsonobj.getPair("encoding"):
            encoding = self.validEncodingPair(jsonobj)
            if encoding == "IEEE754-1985-32":
                ctype = "float"
            elif encoding == "IEEE754-1985-64":
                ctype = "double"
            elif encoding == "twos-complement":
                ctype = "signed long"
            else:
                raise self.ContextLogicError("Illegal encoding property for REAL type", jsonobj)
            
            self.addTypeMetadata(typestring, "encoding", encoding)
        
        return CTypedef(ctype, typestring)
    
    def typeENUMERATED(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        error = self.ContextLogicError("Enumerated strings specification required in format: 'contents':[str1, str2, ...]", jsonobj)
        if not jsonobj.getPair("contents"):
            raise error
        if not jsonobj.getPair("contents").holdsArray():
            raise error
        if not jsonobj.getPairValue("contents").holdsOnlyStrings():
            raise error
        jsonstrings = jsonobj.getPairValue("contents").getElements()
        enumvalues = []
        for jstring in jsonstrings:
            if not validCTypename(jstring.string):
                raise self.ContextLogicError("Enumerated string '{}' is illegal C enum value".format(jstring.string), jsonobj)
            enumvalues.append(jstring.string)
        cenumt = CEnumType(typestring, enumvalues)
        typedef = CTypedef(cenumt, typestring)
        return typedef
    
    def typeSEQUENCE(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        error = self.ContextLogicError("Struct attributes specification required in format: 'contents':[obj1, obj2, ...]", jsonobj)
        if not jsonobj.getPair("contents"):
            raise error
        if not jsonobj.getPair("contents").holdsArray():
            raise error
        if not jsonobj.getPairValue("contents").holdsOnlyObjects():
            raise error
        jsonattrobjs = jsonobj.getPairValue("contents").getElements()
        structattribs = []
        for attribobj in jsonattrobjs:
            attrib = self.validTypeAttribute(attribobj)
            structattribs.append(attrib)
        
        structt = CStructType(typestring, structattribs)
        typedef = CTypedef(structt, typestring)
        return typedef
    
    def typeSEQUENCE_OF(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        
        return
    
    def typeSET(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        
        return
    
    def typeSET_OF(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        
        return
    
    def typeCHOICE(self, jsonobj):
        typestring = self.validTypenamePair(jsonobj)
        
        return
    
    def validTypeAttribute(self, jsonobj, spectype=None):
        typename = self.validTypenamePair(jsonobj)
        attribname = self.validIdentifier(jsonobj, attrib=True)
        if spectype:
            typename = spectype
            
        attrtypedef = None
        if typename == "BOOLEAN":
            attrtypedef = self.typeBOOLEAN(jsonobj)
        elif typename == "INTEGER":
            attrtypedef = self.typeINTEGER(jsonobj)
        elif typename == "REAL":
            attrtypedef = self.typeREAL(jsonobj)
        elif typename == "BIT STRING":
            attrtypedef = self.typeBIT_STRING(jsonobj)
        elif typename == "OCTET STRING":
            attrtypedef = self.typeOCTET_STRING(jsonobj)
        elif typename == "CHARACTER STRING":
            attrtypedef = self.typeCHARACTER_STRING(jsonobj)
        elif typename == "ENUMERATED":
            attrtypedef = self.typeENUMERATED(jsonobj)
        elif typename == "SEQUENCE":
            attrtypedef = self.typeSEQUENCE(jsonobj)
        elif typename == "SEQUENCE OF":
            attrtypedef = self.typeSEQUENCE_OF(jsonobj)
        elif typename == "SET":
            attrtypedef = self.typeSET(jsonobj)
        elif typename == "SET OF":
            attrtypedef = self.typeSET_OF(jsonobj)
        elif typename == "CHOICE":
            attrtypedef = self.typeCHOICE(jsonobj)
        else: #user defined type
            self.checkifTypeDefined(typename, jsonobj)
            return CVarType(typename, attribname)
        attributetype = attrtypedef.covered
        return CVarType(attributetype, attribname)
        
    def validTypenamePair(self, jsonobj):
        attrib = False
        typepair = jsonobj.getPair("typeName")
        if typepair == None:
            typepair = jsonobj.getPair("type")
            attrib = True
        if typepair == None:
            raise self.ContextLogicError("'typeName' or 'type' value should be defined", jsonobj)
        valid = typepair.holdsString()
        if valid:
            typestring = typepair.value.string
            
            # check if typename is valid in C
            if not validCTypename(typestring):
                raise self.ContextLogicError("Type name: '{}' is not valid name for a type".format(typestring), jsonobj)
            return typestring
        else:
            raise self.ContextLogicError("Expected valid 'typeName'/'type' value: <string>", jsonobj)

    def validEncodingPair(self, jsonobj):
        error = self.ContextLogicError("Expected valid 'encoding' property: \"pos-int\", \"twos-complement\"," + \
                            " \"ASCII\",\"IEEE754-1985-32\", \"IEEE754-1985-64\"", jsonobj)
        if jsonobj.getPair("encoding").holdsString():
            encoding = jsonobj.getPairValue("encoding").string
            if encoding not in [ "pos-int", "twos-complement", "ASCII",
                                "IEEE754-1985-32", "IEEE754-1985-64" ]:
                raise error
            return encoding
        else:
            raise error
        
    def validConstraintPair(self, jsonobj, constrType):
        if constrType not in ["min", "max", "size"]:
            return None
        if jsonobj.getPair(constrType).holdsNumber():
            val = jsonobj.getPairValue(constrType).value
            return val
        else:
            raise self.ContextLogicError("Expected valid '{}' value: <integer or real>".format(constrType), jsonobj)
    
    def validIdentifier(self, jsonobj, attrib=False):
        namepair = jsonobj.getPair("objectName")
        if attrib:
            namepair = jsonobj.getPair("attribute")
        
        if namepair != None:
            if not namepair.holdsString():
                raise self.ContextLogicError("Identifier specified in '{}' must be string".format(namepair.name), jsonobj)
        
            if validCidentifier(namepair.value.string):
                return namepair.value.string
            else:
                raise self.ContextLogicError("Identifier '{}' is illegal".format(namepair.value.string), jsonobj)   
        else:
            raise self.ContextLogicError("Identifier should be specified in 'objectName'/'attribute'", jsonobj)
    
    def checkifTypeDefined(self, typename, jsonobj):
        for decl in self.declarations:
            if decl.typename == typename:
                return decl
        raise self.ContextLogicError("Type '{}' is not defined".format(typename), jsonobj)
    
    def addTypeMetadata(self, typestring, name, value):
        if not typestring in self.typesMetadata:
            self.typesMetadata[typestring] = { name:value }
            return
        self.typesMetadata[typestring][name] = value
    
    def ContextLogicError(self, message, jsonobj):
        return LogicError(self.currentFile, message,
                             line=self.enumerated[jsonobj])
        
        
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
    
    print("declatarions------------------------")
    for item in interpr.declarations:
        print(str(item))
        print()
    
    print("defines------------------------")   
    for item in interpr.defines:
        print(str(item))
        print()
    
    print("metadata------------------------")   
    print(interpr.typesMetadata)

    
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
    
    
    
        