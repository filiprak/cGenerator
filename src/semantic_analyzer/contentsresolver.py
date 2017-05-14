'''
Created on 07.05.2017
Contents resolver module aims to read definitions and declarations
from json description and translate them into C types declaration and definition
@author: raqu
'''
from generator.ctypes import CVarType, CTypedef, CPreprocConstDefine, CArrayType,\
    CStructType, CEnumType, CUnionType
from semantic_analyzer.common import asn1types,\
    validCTypename, validCidentifier
from defresolver import DefinitionResolver
from errors import LogicError


class ContentsResolver():
    '''
    Contents resolver is responsible for reading definitions and declarations
    from json description and translating them into C types declaration and definition
    '''
    def __init__(self):
        self.defines = []
        self.declarations = []
        self.definitions = []
        
        self.enumerators = []
        self.defResolver = DefinitionResolver(self.declarations, self.defines, self.enumerators)
        
        self.currentFile = None
        self.currTypename = None
        self.jsonFilelines = None
        
    
    def resolve(self, filesOrder, parsedDict, jsonFilelines):
        '''
        Main resolver function, starts resolving
        :param filesOrder: list of filenames in processing order
        :param parsedDict: dict: key: filename, value: parsed file as JSONObject
        :param jsonFilelines: dict: key: filename, value: dict (key: jsonobj, value: line nr)
        '''
        
        for filename in filesOrder:
            self.currentFile = filename
            self.jsonFilelines = jsonFilelines[filename]
            parsed = parsedDict[filename]
            contentsObjects = self.validModuleContentsPair(parsed)
            
            for jsonobj in contentsObjects:
                if jsonobj.getPair("typeName"):
                    coveredtype = self.validTypenamePair(jsonobj, attrib=True)
                    self.currTypename = self.validTypenamePair(jsonobj)
                    typedef = None
                    if coveredtype == "BOOLEAN":
                        typedef = self.typeBOOLEAN(jsonobj)
                    elif coveredtype == "INTEGER":
                        typedef = self.typeINTEGER(jsonobj)
                    elif coveredtype == "REAL":
                        typedef = self.typeREAL(jsonobj)
                    elif coveredtype == "BIT STRING":
                        typedef = self.typeBIT_STRING(jsonobj)
                    elif coveredtype == "OCTET STRING":
                        typedef = self.typeOCTET_STRING(jsonobj)
                    elif coveredtype == "CHARACTER STRING":
                        typedef = self.typeCHARACTER_STRING(jsonobj)
                    elif coveredtype == "ENUMERATED":
                        typedef = self.typeENUMERATED(jsonobj)
                    elif coveredtype == "SEQUENCE":
                        typedef = self.typeSEQUENCE(jsonobj)
                    elif coveredtype == "SEQUENCE OF":
                        typedef = self.typeSEQUENCE_OF(jsonobj)
                    elif coveredtype == "SET":
                        typedef = self.typeSET(jsonobj)
                    elif coveredtype == "SET OF":
                        typedef = self.typeSET_OF(jsonobj)
                    elif coveredtype == "CHOICE":
                        typedef = self.typeCHOICE(jsonobj)
                    else: #user defined type
                        raise self.ContextLogicError("User defined type '{}' cannot be overriden".format(self.currTypename), jsonobj)
                    if self.checkifTypeDefined(self.currTypename, jsonobj, exception=False) != None:
                        raise self.ContextLogicError("Redeclaration of '{}' type".format(self.currTypename), jsonobj)
                    self.declarations.append(typedef)
                elif jsonobj.getPair("objectName"):
                    defin = self.defResolver.resolve(filename, jsonobj, jsonFilelines)
                    self.definitions.append(defin)
                else:
                    raise self.ContextLogicError("Required 'typeName' or 'objectType' property here", jsonobj)
            
        return self.defines, self.declarations, self.definitions
    
    '''
    This methods resolves single jsonobj user-defined type declarations
    parametres: jsonobj - JSONObject with single declaration of proper covered type
                attrib - 'true' if object have to be treated as inner type attribute
    returns:
                CTypedef object - resolved from JSONObject description of covered
                                ASN.1 types
    '''
    def typeBOOLEAN(self, jsonobj, attrib=False):
        typedef = self.typeINTEGER(jsonobj, attrib)
        optional = dict()
        
        if jsonobj.getPair("true-value"):
            if jsonobj.getPair("true-value").holdsString():
                optional[1] = jsonobj.getPairValue("true-value").string
                typedef.constraints["true-value"] = optional[1]
            else:
                raise self.ContextLogicError("Expected valid 'true-value': <string>", jsonobj)
            
        if jsonobj.getPair("false-value"):
            if jsonobj.getPair("false-value").holdsString():
                optional[0] = jsonobj.getPairValue("false-value").string
                typedef.constraints["false-value"] = optional[0]
            else:
                raise self.ContextLogicError("Expected valid 'false-value': <string>", jsonobj)
            
        for boolvalue in optional.keys():
            # check if typename is valid in C
            if not validCTypename(optional[boolvalue]):
                raise self.ContextLogicError("Type name: '{}' is not valid in C".format(optional[boolvalue]), jsonobj)
            self.defines.append(CPreprocConstDefine(optional[boolvalue], boolvalue))
            
        typedef.constraints["boolean"] = True
        return typedef
    
    def typeINTEGER(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        metadata = dict()            
        if jsonobj.getPair("min"):
            val = self.validConstraintPair(jsonobj, "min")
            metadata["min"] = int(val)
        
        if jsonobj.getPair("max"):
            val = self.validConstraintPair(jsonobj, "max")
            metadata["max"] = int(val)
            
            if "min" in metadata:
                if metadata["min"] > int(val):
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
            
            metadata["encoding"] = encoding
        
        return CTypedef(ctype, typestring, metadata)
    
    def typeBIT_STRING(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        if not jsonobj.getPair("size"):
            raise self.ContextLogicError("Size constraint must be specified for BIT STRING: 'size':<integer>", jsonobj)
        size = self.validConstraintPair(jsonobj, "size")
        nrints = int(size / 32) + 1
        bitarrayt = CArrayType("int", "string", nrints)
        structt = CStructType([bitarrayt], constraints={ "bitstring":True, "size":int(size) })
        typedef = CTypedef(structt, typestring, constraints={ "bitstring":True, "size":int(size) })
        return typedef
    
    def typeCHARACTER_STRING(self, jsonobj, attrib=False):
        typedef = self.typeOCTET_STRING(jsonobj, attrib)
        size = typedef.constraints["size"]
        typedef.constraints = { "charstring":True, "size":size}
        typedef.covered.constraints = { "charstring":True, "size":size }
        return typedef
    
    def typeOCTET_STRING(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        if not jsonobj.getPair("size"):
            raise self.ContextLogicError("Size constraint must be specified for CHAR/OCTET STRING: 'size':<integer>", jsonobj)
        size = self.validConstraintPair(jsonobj, "size")
        
        metadata = dict()
        if jsonobj.getPair("encoding"):
            encoding = self.validEncodingPair(jsonobj)
            if encoding == "ASCII":
                metadata["encoding"] = encoding
            else:
                raise self.ContextLogicError("Illegal encoding property for CHAR/OCTET STRING type", jsonobj)
        
        chararrayt = CArrayType("char", "string", int(size))
        metadata["octetstring"] = True
        metadata["size"] = size
        structt = CStructType([chararrayt], constraints=metadata)
        typedef = CTypedef(structt, typestring, constraints=metadata)
        return typedef
    
    def typeREAL(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        metadata = dict()               
        if jsonobj.getPair("min"):
            val = self.validConstraintPair(jsonobj, "min")
            metadata["min"] = float(val)
        
        if jsonobj.getPair("max"):
            val = self.validConstraintPair(jsonobj, "max")
            metadata["max"] = float(val)
            
            if "min" in metadata:
                if metadata["min"] > float(val):
                    raise self.ContextLogicError("Bad REAL constraints: min > max", jsonobj)
                
        ctype = "double"
        if jsonobj.getPair("encoding"):
            encoding = self.validEncodingPair(jsonobj)
            if encoding == "IEEE754-1985-32":
                ctype = "float"
            elif encoding == "IEEE754-1985-64":
                ctype = "double"
            elif encoding == "twos-complement":
                ctype = "double"
            else:
                raise self.ContextLogicError("Illegal encoding property for REAL type", jsonobj)
            
            metadata["encoding"] = encoding
        
        return CTypedef(ctype, typestring, metadata)
    
    def typeENUMERATED(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        error = self.ContextLogicError("ENUMERATED strings specification required in format: 'enumerators':[str1, str2, ...]", jsonobj)
        if not jsonobj.getPair("enumerators"):
            raise error
        if not jsonobj.getPair("enumerators").holdsArray():
            raise error
        if not jsonobj.getPairValue("enumerators").holdsOnlyStrings():
            raise error
        jsonstrings = jsonobj.getPairValue("enumerators").getElements()
        enumvalues = []
        for jstring in jsonstrings:
            if not validCTypename(jstring.string):
                raise self.ContextLogicError("ENUMERATED string '{}' is illegal value".format(jstring.string), jsonobj)
            if jstring.string in enumvalues:
                raise self.ContextLogicError("ENUMERATED value '{}' duplication".format(jstring.string), jsonobj)
            if jstring.string in self.enumerators:
                raise self.ContextLogicError("ENUMERATED value '{}' redeclaration".format(jstring.string), jsonobj)
            enumvalues.append(jstring.string)
        cenumt = CEnumType(enumvalues)
        typedef = CTypedef(cenumt, typestring)
        self.enumerators += enumvalues
        return typedef
    
    def typeSEQUENCE(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        error = self.ContextLogicError("SEQUENCE attributes specification required in format: 'contents':[obj1, obj2, ...]", jsonobj)
        if not jsonobj.getPair("contents"):
            raise error
        if not jsonobj.getPair("contents").holdsArray():
            raise error
        if not jsonobj.getPairValue("contents").holdsOnlyObjects():
            raise error
        jsonattrobjs = jsonobj.getPairValue("contents").getElements()
        structattribs = []
        attrnames = []
        for attribobj in jsonattrobjs:
            attrib = self.validTypeAttribute(attribobj)
            if attrib.name in attrnames:
                raise self.ContextLogicError("Duplication of SEQUENCE attribute identifiers: {}".format(attrib.name), jsonobj)
            structattribs.append(attrib)
            attrnames.append(attrib.name)
        
        structt = CStructType(structattribs)
        typedef = CTypedef(structt, typestring)
        return typedef
    
    def typeSEQUENCE_OF(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        size = self.validConstraintPair(jsonobj, "size")
        subobj = self.validSubtypePair(jsonobj)
        subattrt = self.validTypeAttribute(subobj, subtype=True)
        constr = dict()
        if subattrt.isSimplType():
            constr = subattrt.constraints
        arrayt = CArrayType(subattrt.variabletype, "elements", int(size), constraints=constr)
        structt = CStructType([ arrayt ])
        return CTypedef(structt, typestring)
    
    def typeSET(self, jsonobj, attrib=False):
        return self.typeSEQUENCE(jsonobj, attrib)
    
    def typeSET_OF(self, jsonobj, attrib=False):
        return self.typeSEQUENCE_OF(jsonobj, attrib)
    
    def typeCHOICE(self, jsonobj, attrib=False):
        typestring = self.validTypenamePair(jsonobj, attrib)
        error = self.ContextLogicError("CHOICE attributes specification required in format: 'contents':[obj1, obj2, ...]", jsonobj)
        if not jsonobj.getPair("contents"):
            raise error
        if not jsonobj.getPair("contents").holdsArray():
            raise error
        if not jsonobj.getPairValue("contents").holdsOnlyObjects():
            raise error
        jsonattrobjs = jsonobj.getPairValue("contents").getElements()
        unionattribs = []
        attrnames = []
        for attribobj in jsonattrobjs:
            attrib = self.validTypeAttribute(attribobj)
            if attrib.name in attrnames:
                raise self.ContextLogicError("Duplication of CHOICE attribute identifiers: {}".format(attrib.name), jsonobj)
            unionattribs.append(attrib)
            attrnames.append(attrib.name)
            
        uniont = CUnionType(unionattribs)
        typedef = CTypedef(uniont, typestring)
        return typedef
    
    '''
    This methods helps with validating if JSONPairs value and structure are as wanted
    
    '''
    def validTypeAttribute(self, jsonobj, spectype=None, subtype=False):
        '''
        Validates attribute of structured type, if correct returns it,
        otherwise raise an exception
        :param jsonobj: JSONObject with attribute description
        :param spectype: specified type (string) optional, used if attribute type have to be forced
        :param subtype: 'true' if attribute is subtype of SEQUENCE OF or SET OF
        '''
        typename = spectype
        attribname = "default"
        if spectype == None:
            if not subtype:
                attribname = self.validIdentifier(jsonobj, attrib=True)
            typename = self.validTypenamePair(jsonobj, attrib=True)
            
        attrtypedef = None
        if typename == "BOOLEAN":
            attrtypedef = self.typeBOOLEAN(jsonobj, attrib=True)
        elif typename == "INTEGER":
            attrtypedef = self.typeINTEGER(jsonobj, attrib=True)
        elif typename == "REAL":
            attrtypedef = self.typeREAL(jsonobj, attrib=True)
        elif typename == "BIT STRING":
            attrtypedef = self.typeBIT_STRING(jsonobj, attrib=True)
        elif typename == "OCTET STRING":
            attrtypedef = self.typeOCTET_STRING(jsonobj, attrib=True)
        elif typename == "CHARACTER STRING":
            attrtypedef = self.typeCHARACTER_STRING(jsonobj, attrib=True)
        elif typename == "ENUMERATED":
            attrtypedef = self.typeENUMERATED(jsonobj, attrib=True)
        elif typename == "SEQUENCE":
            attrtypedef = self.typeSEQUENCE(jsonobj, attrib=True)
        elif typename == "SEQUENCE OF":
            attrtypedef = self.typeSEQUENCE_OF(jsonobj, attrib=True)
        elif typename == "SET":
            attrtypedef = self.typeSET(jsonobj, attrib=True)
        elif typename == "SET OF":
            attrtypedef = self.typeSET_OF(jsonobj, attrib=True)
        elif typename == "CHOICE":
            attrtypedef = self.typeCHOICE(jsonobj, attrib=True)
        else: #user defined type
            if typename == self.currTypename:
                raise self.ContextLogicError("Recursive types are not supported: '{}'".format(typename), jsonobj)
            typedef = self.checkifTypeDefined(typename, jsonobj)
            return CVarType(typedef.covered, attribname, constraints=typedef.constraints)
        attributetype = attrtypedef.covered
        return CVarType(attributetype, attribname, constraints=attrtypedef.constraints)
    
    def validSubtypePair(self, jsonobj):
        '''
        Validates subtype pair structure and returns it value if correct,
        otherwise raises an exception
        :param jsonobj:
        '''
        subtypepair = jsonobj.getPair("subtype")
        if subtypepair == None:
            raise self.ContextLogicError("'subtype' specification is required here", jsonobj)
        valid = subtypepair.holdsObject()
        if valid:
            return subtypepair.value
        raise self.ContextLogicError("'subtype' property should hold JSON object value", jsonobj)
        
    def validTypenamePair(self, jsonobj, attrib=False, subtype=False):
        '''
        Validates typename pair, checks if it holds correct string value
        typename pair can be tagged: "typeName", "type" or "subtype"
        '''
        typetag = "typeName"
        if attrib:
            typetag = "type"
        if subtype:
            typetag = "subtype"
        typepair = jsonobj.getPair(typetag)
        
        if typepair == None:
            raise self.ContextLogicError("'{}' specification is required here".format(typetag), jsonobj)
        valid = typepair.holdsString()
        if valid:
            typestring = typepair.value.string
            # if attribute then allow for asn1 built-in types
            if (attrib or subtype) and typestring in asn1types:
                return typestring
            # check if typename is valid in C
            if not validCTypename(typestring):
                raise self.ContextLogicError("Type name: '{}' is not valid name for a type".format(typestring), jsonobj)
            return typestring
        else:
            raise self.ContextLogicError("Expected valid '{}' value: <string>".format(typetag), jsonobj)

    def validEncodingPair(self, jsonobj):
        '''
        Validates encoding pair, checks if it holds one of allowed values
        '''
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
        '''
        Validates constraint pairs: "min", "max", "size" properties
        :param constrType: type of constraint to check
        '''
        error = self.ContextLogicError("Expected valid '{}' value: <integer or real>".format(constrType), jsonobj)
        if constrType not in ["min", "max", "size"]:
            return None
        pair = jsonobj.getPair(constrType)
        if not pair:
            raise error
        if pair.holdsNumber():
            val = jsonobj.getPairValue(constrType).value
            if constrType == "size" and ( jsonobj.getPairValue(constrType).isFloat() or val < 1 ):
                raise self.ContextLogicError("'size' property must have positive <integer> value", jsonobj)
            return val
        else:
            raise error
        
    def validIdentifier(self, jsonobj, attrib=False):
        '''
        Validates "objectName" pair, checks if contains allowed value
        '''
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
    
    def checkifTypeDefined(self, typename, jsonobj, exception=True):
        '''
        Checks if type is already on declarations list
        :param typename: type to check
        '''
        for decl in self.declarations:
            if decl.typename == typename:
                return decl
        if exception:
            raise self.ContextLogicError("Type '{}' is not defined".format(typename), jsonobj)
        return None
    
    def validModuleContentsPair(self, jsonobj):
        '''
        Validates structure of "moduleContents" pair
        '''
        error = self.ContextLogicError("Wrong format or missing module contents: " +\
                                       "expected format: 'moduleContents':[obj1, obj2, ...]", jsonobj)
        contPair = jsonobj.getPair("moduleContents")
        if not contPair:
            raise error
        if not contPair.holdsArray():
            raise error
        if not contPair.value.holdsOnlyObjects():
            raise error
        return contPair.value.getElements()
    
    def ContextLogicError(self, message, jsonobj):
        '''
        Creates exception instance in context of file, and currently analysed json object
        :param message: message to pass
        :param jsonobj: context JSONObject
        '''
        return LogicError(self.currentFile, message,
                             line=self.jsonFilelines[jsonobj])
