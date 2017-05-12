'''
Created on 10.05.2017
Module contains one class responsible for variable definition (initialization)
resolving from json ASN.1 descriptions
@author: raqu
'''
from errors import LogicError
from semantic_analyzer.common import asn1types, validCidentifier
from generator.cassigns import CVarAssign
from generator.ctypes import CVarType
from pip.cmdoptions import constraints


class DefinitionResolver():
    '''
    Responsible for variable definition (initialization)
    resolving from json ASN.1 descriptions
    '''
    def __init__(self, declarations, defines):
        '''
        :param declarations: list containing CTypedef, CVarType type elements
        :param defines: list containing CPreprocConstDefine type elements
        '''
        self.declarations = declarations
        self.defines = defines
        self.definitions = []
        self.jsonFilelines = None
        self.currentFile = None
        self.currObject = None
        
    def resolve(self, filename, jsonobj, jsonFilelines):
        '''
        Methods perform single jsonobj resolving
        :param filename: name of resolved file
        :param jsonobj: JSONObject with definiton desctription
        :param jsonFilelines: dict: key: file name,
                value: dict: (key: jsonobj, value: its line number in file)
        '''
        # setup context
        self.currentFile = filename
        self.jsonFilelines = jsonFilelines[filename]
        self.currObject = jsonobj
        
        definition = None
        
        identifier = self.validPair(jsonobj, "objectName", expvalue=["string"])
        if not validCidentifier(identifier):
            raise self.ContextLogicError("Illegal identifier for object: '{}'".format(identifier), jsonobj)
        if self.checkIfobjectDefined(identifier, exception=False) != None:
            raise self.ContextLogicError("Object '{}' is already defined".format(identifier), jsonobj)
        objtype = self.validPair(jsonobj, "type", expvalue=["string"])
        print(objtype)
        if objtype in asn1types:
            raise
        else:
            typedef = self.checkIftypeDeclared(objtype)
            covered = typedef.covered
            constr = typedef.constraints
            
            if isinstance(covered, str):
                definition = self.assignSimpleType(jsonobj, covered,
                                                   identifier, constr, typedef=typedef.typename)
                
        if definition:
            self.definitions.append(definition)
        return definition
    
    def assignSimpleType(self, jsonobj, simpltype, ident, constr, attrib=False, typedef=None):
        objecttype = CVarType(simpltype, ident, constr)
        if typedef != None:
            objecttype = CVarType(typedef, ident, constr)
        # int as boolean value
        if simpltype == "int" and "boolean" in constr:
            value = self.validPair(jsonobj, "value", expvalue=["string", "literal"])
            if value not in [ "false", "true" ]:
                if "true-value" in constr:
                    if value == constr["true-value"]:
                        return CVarAssign(objecttype, value, attrib)
                elif "false-value" in constr:
                    if value == constr["false-value"]:
                        return CVarAssign(objecttype, value, attrib)
                raise self.ContextLogicError("Illegal object value, expected boolean value", jsonobj)
            if value == "true":
                return CVarAssign(objecttype, 1, attrib)
            return CVarAssign(objecttype, 0, attrib)
            
        # number value
        inttypes = ["int", "unsigned"]
        floattypes = ["double", "float"]   
        if simpltype in inttypes or simpltype in floattypes:
            value = 0
            if simpltype in inttypes:
                value = self.validPair(jsonobj, "value", expvalue=["string", "int"])
            if simpltype in floattypes:
                value = self.validPair(jsonobj, "value", expvalue=["string", "float"])  
            if isinstance(value, str):
                defin = self.checkIfobjectDefined(value)
                if not isinstance(defin, CVarAssign):
                    raise self.ContextLogicError("Incompatibile type for assignment in 'value'", jsonobj)
                if defin.vartype.variabletype == simpltype:
                    return CVarAssign(objecttype, value, attrib)
                if defin.vartype.variabletype == simpltype and defin.vartype.constraints == constr:
                    return CVarAssign(objecttype, value, attrib)
            self.checkNumberConstr(jsonobj, ident, value, constr)
            return CVarAssign(objecttype, value, attrib)

    
    def assignAttribute(self, jsonobj, cvartype):
        return
    
    '''
    This methods helps with validating if JSONPairs value and structure are as wanted
    
    '''
    def checkNumberConstr(self, jsonobj, ident, value, constraints):
        if "min" in constraints:
            if value < constraints["min"]:
                raise self.ContextLogicError("Value of "+\
                    "'{}' has constraint: min={}".format(ident, str(constraints["min"])), jsonobj)
        if "max" in constraints:
            if value > constraints["max"]:
                raise self.ContextLogicError("Value of "+\
                    "'{}' has constraint: max={}".format(ident, str(constraints["max"])), jsonobj)
        if "encoding" in constraints:
            if constraints["encoding"] == "pos-int":
                if value < 1:
                    raise self.ContextLogicError("Value of '{}' "+\
                        "has constraint: pos-int (positive int)".format(ident), jsonobj)
        return True
    
    def checkIfobjectDefined(self, identifier, exception=True):
        for defin in self.definitions:
            if defin.name == identifier:
                return defin
        if exception:
            raise self.ContextLogicError("Variable '{}' is not defined anywhere".format(identifier), self.currObject)
        return None
    
    def checkIftypeDeclared(self, typename, exception=True):
        for typedef in self.declarations:
            if typedef.typename == typename:
                return typedef
        if exception:
            raise self.ContextLogicError("Type '{}' is not defined anywhere".format(typename), self.currObject)
        return None
    
    def validPair(self, jsonobj, name, expvalue=[]):
        
        error = self.ContextLogicError("Missing or incorrect value" + \
                                       " '{}', allowed value types {}".format(name, str(expvalue)), jsonobj)
        pair = jsonobj.getPair(name)
        if not pair:
            raise error
        if "string" in expvalue and pair.holdsString():
            return pair.value.string
        elif "int" in expvalue and pair.holdsNumber(numtype="int"):
            return pair.value.value
        elif "float" in expvalue and pair.holdsNumber(numtype="float"):
            return pair.value.value
        elif "object" in expvalue and pair.holdsObject():
            return pair.value
        elif "array" in expvalue and pair.holdArray():
            return pair.value.getElements()
        elif "literal" in expvalue and pair.holdsLiteral():
            return pair.value.literal
        elif len(expvalue) == 0:
            return pair.value
        raise error
        
    
    def ContextLogicError(self, message, jsonobj):
        return LogicError(self.currentFile, message, self.jsonFilelines[jsonobj])
    
    