'''
Created on 10.05.2017
Module contains one class responsible for variable definition (initialization)
resolving from json ASN.1 descriptions
@author: raqu
'''
from errors import LogicError


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
        self.jsonFilelines = jsonFilelines
        self.currObject = jsonobj
        
        definition = ""
        
        self.definitions.append(definition)
        return definition
    
    '''
    This methods helps with validating if JSONPairs value and structure are as wanted
    
    '''
    def validPair(self, name, expvalue="string"):
        error = self.ContextLogicError("Missing or incorrect value '{}', expected <{}> value".format(name, expvalue))
        pair = self.currObject.getPair(name)
        if not pair:
            raise error
        if expvalue == "string" and pair.holdsString():
            return pair.value.string
        elif expvalue == "int" and pair.holdsNumber(numtype="int"):
            return pair.value.value
        elif expvalue == "float" and pair.holdsNumber(numtype="float"):
            return pair.value.value
        elif expvalue == "object" and pair.holdsObject():
            return pair.value
        elif expvalue == "array" and pair.holdArray():
            return pair.value.getElements()
        elif expvalue == "literal" and pair.holdsLiteral():
            return pair.value.literal
        raise error
        
    
    def ContextLogicError(self, message):
        return LogicError(self.currentFile, message, self.jsonFilelines[self.currObject])
    
    