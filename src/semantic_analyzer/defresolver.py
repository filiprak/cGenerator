'''
Created on 10.05.2017
Module contains one class responsible for variable definition (initialization)
resolving from json ASN.1 descriptions
@author: raqu
'''
from errors import LogicError
from semantic_analyzer.common import asn1types, validCidentifier, floatctypes,\
    intctypes
from generator.cassigns import CVarAssign, CArrayAssign, CUnionAssign,\
    CEnumAssign, CStructAssign
from generator.ctypes import CVarType, CStructType, CEnumType, CUnionType,\
    CArrayType, CTypedef
from jsonparser.jsontypes import JSONString, JSONObject, JSONNumber, JSONLiteral
import math


class DefinitionResolver():
    '''
    Responsible for variable definition (initialization)
    resolving from json ASN.1 descriptions
    '''
    def __init__(self, declarations, defines, enumerators):
        '''
        :param declarations: list containing CTypedef, CVarType type elements
        :param defines: list containing CPreprocConstDefine type elements
        '''
        self.declarations = declarations
        self.defines = defines
        self.enumerators = enumerators
        self.definitions = []
        self.jsonFilelines = None
        self.currentFile = None
        self.currObject = None
        self.currAssignedType = None
        
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
        
        # result object
        definition = None
        
        # read identifier and type of object
        identifier = self.validPair(jsonobj, "objectName", expvalue=["string"])
        if not validCidentifier(identifier):
            raise self.ContextLogicError("Illegal identifier for object: '{}'".format(identifier), jsonobj)
        if self.checkIfobjectDefined(identifier, exception=False) != None:
            raise self.ContextLogicError("Object '{}' is already defined".format(identifier), jsonobj)
        objtype = self.validPair(jsonobj, "type", expvalue=["string"])
        self.currAssignedType = objtype
        
        # if asn1 built-in type
        if objtype in asn1types:
            if objtype == "INTEGER":
                definition = self.assignSimpleType(jsonobj, "int", identifier, dict())
            elif objtype == "REAL":
                definition = self.assignSimpleType(jsonobj, "double", identifier, dict())
            elif objtype == "BOOLEAN":
                definition = self.assignSimpleType(jsonobj, "int", identifier, { "boolean":True })
            elif objtype == "BIT STRING":
                size = self.validPair(jsonobj, "size", expvalue=["int"])
                arrayt = CArrayType("int", "string", int(math.ceil(float(size)/32)))
                arrassign = self.assignArrayType(jsonobj, arrayt, "string", { "bitstring":True, "size":size })
                structt = CStructType([arrayt])
                definition = CStructAssign(structt, identifier, { "string":arrassign.values }, inline=True)
            elif objtype == "OCTET STRING":
                size = self.validPair(jsonobj, "size", expvalue=["int"])
                arrayt = CArrayType("char", "string", int(size))
                arrassign = self.assignArrayType(jsonobj, arrayt, "string", { "octetstring":True, "size":size })
                structt = CStructType([arrayt])
                definition = CStructAssign(structt, identifier, { "string":arrassign.values }, inline=True)
            elif objtype == "CHARACTER STRING":
                size = self.validPair(jsonobj, "size", expvalue=["int"])
                arrayt = CArrayType("char", "string", int(size))
                arrassign = self.assignArrayType(jsonobj, arrayt, "string", { "charstring":True, "size":size })
                structt = CStructType([arrayt])
                definition = CStructAssign(structt, identifier, { "string":arrassign.values }, inline=True)
            elif objtype == "ENUMERATED":
                values = self.validPair(jsonobj, "enumerators", expvalue=["array of strings"])
                for v in values:
                    if self.checkIfobjectDefined(v, exception=False) != None or v == identifier:
                        raise self.ContextLogicError("Enum value '{}' duplicates".format(v) +\
                                                     " defined object identifier", jsonobj)
                    if v in self.enumerators:
                        raise self.ContextLogicError("Redeclaration of ENUMERATED value '{}'".format(v), jsonobj)
                    if not validCidentifier(v):
                        raise self.ContextLogicError("Illegal enumerator of ENUMERATED type '{}'".format(v), jsonobj)
                enumt = CEnumType(values)
                self.enumerators += values
                definition = self.assignEnumType(jsonobj, enumt, identifier, dict(), inline=True)
            else:
                raise self.ContextLogicError("Type '{}' is not supported".format(objtype) +\
                                " for direct variable initialization", jsonobj)
                
        else: # if user-defined type
            definition = self.assignUserDefinedType(jsonobj, objtype, identifier)
            
        if definition:
            self.definitions.append(definition)
        return definition
    
    def assignUserDefinedType(self, jsonobj, usertype, identifier, attrib=False):
        '''
        Assigns object which type is user-defined
        :param jsonobj: object that contain value specification
        :param usertype: string of type declared by user
        :param identifier: object identifier
        :param attrib: flag, tells if object is attribute of some structural type
        '''
        typedef = self.checkIftypeDeclared(usertype)
        covered = typedef.covered
        constr = typedef.constraints
        definition = None

        # check if type recursivly assigned
        if attrib and self.currAssignedType == usertype:
            nulllit = self.validPair(jsonobj, identifier, expvalue=["null"], exception=False)
            if nulllit == "null":
                return None
        # if user-defined type is simple type based
        if typedef.coverSimplType():
            definition = self.assignSimpleType(jsonobj, covered,
                                               identifier, constr=constr, attrib=attrib, typedef=typedef.typename)
            
        #if user-defined type is structural type based
        elif isinstance(covered, CStructType):
            
            definition = self.assignStructType(jsonobj, covered, 
                                               identifier, constr, attrib=attrib, typedef=typedef.typename)
        
        elif isinstance(covered, CUnionType):
            definition = self.assignUnionType(jsonobj, covered, 
                                               identifier, constr, attrib=attrib, typedef=typedef.typename)
        
        elif isinstance(covered, CEnumType):
            definition = self.assignEnumType(jsonobj, covered,
                                               identifier, constr, attrib=attrib, typedef=typedef.typename)
        else:
            raise self.ContextLogicError("Internal error. Unknown type covered by typedef", jsonobj)
    
        return definition
        
    def assignSimpleType(self, jsonobj, simpltype, ident, constr,
                         attrib=False, typedef=None, arrayelem=(False, None)):
        '''
        Assigns simple typed object, simple type is one of int, unsigned, double or float
        :param jsonobj: object that contain value specification
        :param simpltype: one of int, unsigned, double or float
        :param ident: object identifier
        :param constr: dict of constraints for object
        :param attrib: flag, tells if object is attribute of some structural type
        :param typedef: string type that covers simple type
        :param arrayelem: flag, tells if object is array element
        '''
        valpairname = "value"
        if attrib:
            valpairname = ident
        
        isarrayelement, value = arrayelem
        
        objecttype = CVarType(simpltype, ident, constr, alias=typedef)
        # int as boolean value
        if simpltype == "int" and "boolean" in constr:
            if not isarrayelement:
                value = self.validPair(jsonobj, valpairname, expvalue=["string", "literal"])
            if value not in [ "false", "true" ]:
                if "true-value" in constr:
                    if value == constr["true-value"]:
                        return CVarAssign(objecttype, value, attrib, typedef=typedef)
                if "false-value" in constr:
                    if value == constr["false-value"]:
                        return CVarAssign(objecttype, value, attrib, typedef=typedef)
                defin = self.checkIfobjectDefined(value, objtype=CVarAssign)
                if "boolean" not in defin.vartype.constraints:
                    raise self.ContextLogicError("Illegal object value, expected BOOLEAN value", jsonobj)
                return CVarAssign(defin.vartype, value, attrib=attrib, typedef=typedef)
            elif value == "true":
                return CVarAssign(objecttype, 1, attrib=attrib, typedef=typedef)
            elif value == "false":
                return CVarAssign(objecttype, 0, attrib=attrib, typedef=typedef)
            else:
                raise self.ContextLogicError("Illegal object value, expected BOOLEAN value", jsonobj)
            
        # number value   
        if simpltype in intctypes or simpltype in floatctypes:
            if simpltype in intctypes and not isarrayelement:
                value = self.validPair(jsonobj, valpairname, expvalue=["string", "int"])
            if simpltype in floatctypes and not isarrayelement:
                value = self.validPair(jsonobj, valpairname, expvalue=["string", "float"])  
            if isinstance(value, str):
                defin = self.checkIfobjectDefined(value, objtype=CVarAssign)
                if not defin.typedef == typedef:
                    raise self.ContextLogicError("Incompatible type for number assignment: '{}'".format(value), jsonobj)
                elif defin.vartype.variabletype == simpltype and defin.vartype.constraints == constr:
                    return CVarAssign(objecttype, value, attrib=attrib, typedef=typedef)
                else:
                    raise self.ContextLogicError("Incompatible type for number assignment: '{}'".format(value), jsonobj)
            self.checkNumberConstr(jsonobj, ident, value, constraints=constr)
            return CVarAssign(objecttype, value, attrib=attrib, typedef=typedef)
        
        raise self.ContextLogicError("Internal error. Trying to assign non simple-type object", jsonobj)
        
    def assignStructType(self, jsonobj, cstructtype, ident, constr, attrib=False, typedef=None, inline=False):
        '''
        Assigns struct type
        :param jsonobj: object that contain value specification
        :param ident: object identifier
        :param constr: dict of constraints for object
        :param attrib: flag, tells if object is attribute of some structural type
        :param typedef: string type that covers simple type
        :param cstructtype: CStructType object that specifies struct type

        '''
        valpairname = "value"
        if attrib:
            valpairname = ident
        
        validvalues = dict()
        jsonstr = self.validPair(jsonobj, valpairname)
        if isinstance(jsonstr, JSONString):
            obj = self.checkIfobjectDefined(jsonstr.string, objtype=CStructAssign)
            if obj.typedef == typedef:
                return CStructAssign(cstructtype, ident, jsonstr.string, typedef=typedef, attrib=attrib)
        jsonvalues = self.validPair(jsonobj, valpairname, expvalue=["object"])

        for a in cstructtype.attributes:
            if not isinstance(a, (CVarType, CArrayType)):
                raise self.ContextLogicError("Internal error: illegal struct member in: \n" +\
                                              str(cstructtype), jsonobj)
            if isinstance(a, CVarType):
                if isinstance(a.variabletype, CStructType):
                    
                    strassign = self.assignStructType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)
                    validvalues[a.name] = strassign.value
                elif isinstance(a.variabletype, CEnumType):
                    enumassign = self.assignEnumType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)                    
                    validvalues[a.name] = enumassign.value
                elif isinstance(a.variabletype, CUnionType):
                    uniassign = self.assignUnionType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)                    
                    validvalues[a.name] = uniassign.value
                elif a.isSimplType():
                    simpleassign = self.assignSimpleType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)
                    validvalues[a.name] = simpleassign.value
                elif isinstance(a.variabletype, str):
                    usrdefined = self.assignUserDefinedType(jsonvalues, a.variabletype, a.name, attrib=True)
                    if usrdefined:
                        validvalues[a.name] = usrdefined.value
                else:
                    raise self.ContextLogicError("Internal error. Trying to assign unknown type object", jsonobj)
                
            elif isinstance(a, CArrayType):
                arrasign = self.assignArrayType(jsonvalues, a, a.name, constr, attrib=True)
                validvalues[a.name] = arrasign.values
                
        return CStructAssign(cstructtype, ident, validvalues, typedef=typedef, attrib=attrib, inline=inline)
    
    def assignUnionType(self, jsonobj, cuniontype, ident, constr, attrib=False, typedef=None, inline=False):
        '''
        Assigns union type object
        :param jsonobj: object that contain value specification
        :param cuniontype: CUnionType object that specifies union type
        :param ident: object identifier
        :param constr: dict of constraints for object
        :param attrib: flag, tells if object is attribute of some structural type
        :param typedef: string type that covers simple type
        :param arrayelem: flag, tells if object is array element
        '''
        valpairname = "value"
        if attrib:
            valpairname = ident
        
        validvalue = dict()
        jsonstr = self.validPair(jsonobj, valpairname)
        if isinstance(jsonstr, JSONString):
            obj = self.checkIfobjectDefined(jsonstr.string, objtype=CUnionAssign)
            if obj.typedef == typedef:
                return CUnionAssign(cuniontype, ident, jsonstr.string, typedef=typedef, attrib=attrib)
        jsonvalues = self.validPair(jsonobj, valpairname, expvalue=["object"])
        propertynames = jsonvalues.getPairNames()

        if len(propertynames) != 1:
            raise self.ContextLogicError("One of CHOICE object attributes should be assigned", jsonobj)
        attr = propertynames[0]
        for a in cuniontype.attributes:
            if a.name != attr:
                continue
            if not isinstance(a, (CVarType, CArrayType)):
                raise self.ContextLogicError("Internal error: illegal union member in: \n" +\
                                              str(cuniontype), jsonobj)
            if isinstance(a, CVarType):
                if isinstance(a.variabletype, CStructType):
                    strassign = self.assignStructType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)                    
                    validvalue[a.name] = strassign.value
                elif isinstance(a.variabletype, CEnumType):
                    enumassign = self.assignEnumType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)                    
                    validvalue[a.name] = enumassign.value
                elif isinstance(a.variabletype, CUnionType):
                    uniassign = self.assignUnionType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)                    
                    validvalue[a.name] = uniassign.value
                elif a.isSimplType():
                    simpleassign = self.assignSimpleType(jsonvalues, a.variabletype,
                        a.name, constr=a.constraints, typedef=a.alias, attrib=True)                    
                    validvalue[a.name] = simpleassign.value
                elif isinstance(a.variabletype, str):
                    usrdefined = self.assignUserDefinedType(jsonvalues, a.variabletype, a.name, attrib=True)
                    if usrdefined:
                        validvalue[a.name] = usrdefined.value
                else:
                    raise self.ContextLogicError("Internal error. Trying to assign unknown type object", jsonobj)
                
            elif isinstance(a, CArrayType):
                arrasign = self.assignArrayType(jsonvalues, a, a.name, constr, attrib=True)
                validvalue[a.name] = arrasign.values
                
            return CUnionAssign(cuniontype, ident, validvalue, typedef=typedef, attrib=attrib, inline=inline)
        raise self.ContextLogicError("CHOICE assign failed, attribute '{}' does not exist".format(attr), jsonobj)
    
    def assignEnumType(self, jsonobj, cenumtype, ident, constr, attrib=False, typedef=None, inline=False):
        '''
        Assigns enum type object
        :param jsonobj: object that contain value specification
        :param cenumtype: CEnumType object that specifies enum type
        :param ident: object identifier
        :param constr: dict of constraints for object
        :param attrib: flag, tells if object is attribute of some structural type
        :param typedef: string type that covers simple type
        :param arrayelem: flag, tells if object is array element
        '''
        valpairname = "value"
        if attrib:
            valpairname = ident
        
        val = self.validPair(jsonobj, valpairname, expvalue=["string"])
        if val in cenumtype.values:
            return CEnumAssign(cenumtype, ident, val, attrib=attrib, typedef=typedef,inline=inline)
        
        obj = self.checkIfobjectDefined(val, objtype=CEnumAssign)

        if obj.typedef == typedef:
            return CEnumAssign(cenumtype, ident, val, attrib=attrib, typedef=typedef,inline=inline)
        raise self.ContextLogicError("Variable '{}' has incompatible value type".format(val), jsonobj)

    def assignArrayType(self, jsonobj, carraytype, ident, constr, attrib=False):
        '''
        Assigns array type object
        :param jsonobj: object that contain value specification
        :param carraytype: CArrayType that specifies array object type
        :param ident: object identifier
        :param constr: dict of constraints for object
        :param attrib: flag, tells if object is attribute of some structural type
        '''
        valpairname = "value"
        if attrib:
            valpairname = ident
        
        # when bit/octet/char string type
        if "bitstring" in constr:
            value = self.validPair(jsonobj, valpairname, expvalue=["string"])
            arrayvalues = self.bitStringStrip(jsonobj, value, 32, constr["size"])
            return CArrayAssign(carraytype, arrayvalues, attrib)
        if "octetstring" in constr:
            value = self.validPair(jsonobj, valpairname, expvalue=["string"])
            arrayvalues = self.bitStringStrip(jsonobj, value, 8, carraytype.size*8)
            return CArrayAssign(carraytype, arrayvalues, attrib)
        if "charstring" in constr:
            value = self.validPair(jsonobj, valpairname, expvalue=["string"])
            if len(value) != carraytype.size:
                raise self.ContextLogicError("CHARACTER STRING incompatible length string assigned", jsonobj)
            return CArrayAssign(carraytype, value, attrib)
        
        if not attrib:
            valpairname = "values"
        
        # when element type is number simpletype: int / float / unsigned / double
        if carraytype.isSimplType():
            validvalues = []
            values = self.validPair(jsonobj, valpairname, expvalue=["array"])
            if len(values) != carraytype.size:
                raise self.ContextLogicError("Expected {} elements in array initializer".format(carraytype.size), jsonobj)
            for obj in values:
                val = None
                if isinstance(obj, JSONString):
                    val = obj.string
                elif isinstance(obj, JSONNumber):
                    if carraytype.valtype in intctypes and obj.isFloat():
                        raise self.ContextLogicError("Expected INTEGER array-element values", jsonobj)
                    if carraytype.valtype in floatctypes and obj.isInteger():
                        raise self.ContextLogicError("Expected REAL array-element values", jsonobj)
                    val = obj.value
                elif isinstance(obj, JSONLiteral):
                    val = obj.literal
                else:
                    self.ContextLogicError("Incomatible type of array element value", jsonobj)
                cvarassign = self.assignSimpleType(jsonobj, carraytype.valtype, "array-element",
                                  constr=carraytype.constraints, typedef=carraytype.alias,
                                  attrib=attrib, arrayelem=(True, val))
                validvalues.append(cvarassign.value)
            
            return CArrayAssign(carraytype, validvalues, attrib=attrib)
        
        # when element type is used-defined type. First find typedef declaration
        typedef = CTypedef(carraytype.valtype, "-inner-struct", constraints=carraytype.constraints)
        if isinstance(carraytype.valtype, str):
            typedef = self.checkIftypeDeclared(carraytype.valtype) 
        
        # user-type is based on some simple type
        if typedef.coverSimplType():
            carraytype.valtype = typedef.covered
            return self.assignArrayType(jsonobj, carraytype, ident, typedef.constraints, attrib)
        
        # user-type is based on structural type: typedef covers CStructType, CEnumType or CUnionType
        uncoveredtype = typedef.covered
        cnames = carraytype.constraints.keys()
        
        values = None
        # assign of string type
        if "charstring" in cnames or "bitstring" in cnames or "octetstring" in cnames:
            values = self.validPair(jsonobj, valpairname, expvalue=["array of strings"])
            if len(values) != carraytype.size:
                raise self.ContextLogicError(
                    "Array '{}' should have {} elements".format(carraytype.name, carraytype.size), jsonobj)
        
        if "charstring" in carraytype.constraints:
            arrayvalues = []
            for v in values:
                if len(v) != carraytype.constraints["size"]:
                    raise self.ContextLogicError("CHARACTER STRING incompatible length string assigned", jsonobj)
                strassign = CStructAssign(uncoveredtype, "charstr", { "string":v }, semicol=False, attrib=True)
                strassign.arrayelement = True
                arrayvalues.append(strassign)
            return CArrayAssign(carraytype, arrayvalues, attrib=attrib)
        
        if "bitstring" in carraytype.constraints:
            arrayvalues = []
            size = carraytype.constraints["size"]
            for v in values:
                subarrayvalues = self.bitStringStrip(jsonobj, v, 32, size)
                strassign = CStructAssign(uncoveredtype, "bitstr", { "string":subarrayvalues }, semicol=False, attrib=True)
                strassign.arrayelement = True
                arrayvalues.append(strassign)
            return CArrayAssign(carraytype, arrayvalues, attrib=attrib)
        
        if "octetstring" in carraytype.constraints:
            arrayvalues = []
            size = carraytype.constraints["size"]
            for v in values:
                subarrayvalues = self.bitStringStrip(jsonobj, v, 8, size*8)
                strassign = CStructAssign(uncoveredtype, "octstr", { "string":subarrayvalues }, semicol=False, attrib=True)
                strassign.arrayelement = True
                arrayvalues.append(strassign)
            return CArrayAssign(carraytype, arrayvalues, attrib=attrib)
        
        # user-defined type but not simple type and not string type
        values = self.validPair(jsonobj, valpairname, expvalue=["array"])
        if len(values) != carraytype.size:
            raise self.ContextLogicError(
                "Array '{}' should have {} elements".format(carraytype.name, carraytype.size), jsonobj)
            
        validvalues = []
        if isinstance(uncoveredtype, CStructType):
            for obj in values:
                if isinstance(obj, JSONString):
                    defin = self.checkIfobjectDefined(obj.string, objtype=CStructAssign)
                    if defin.typedef == carraytype.alias:
                        validvalues.append(defin.name)
                    else:
                        raise self.ContextLogicError("Incompatible array value assignment", jsonobj)
                elif isinstance(obj, JSONObject):
                    structassign = self.assignStructType(obj, uncoveredtype, "value", constr, attrib=attrib)
                    structassign.arrayelement = True
                    validvalues.append(structassign)
                else:
                    raise self.ContextLogicError("Incompatible array value assignment"+\
                                ", note value is type '{}'".format(defin.typedef), jsonobj)
            return CArrayAssign(carraytype, validvalues, attrib=attrib)
            
        elif isinstance(uncoveredtype, CUnionType):
            for obj in values:
                if isinstance(obj, JSONString):
                    defin = self.checkIfobjectDefined(obj.string, objtype=CStructAssign)
                    if defin.typedef == carraytype.alias:
                        validvalues.append(defin.name)
                    else:
                        raise self.ContextLogicError("Incompatible array value assignment"+\
                                ", note value is type '{}'".format(defin.typedef), jsonobj)
                elif isinstance(obj, JSONObject):
                    unionassign = self.assignUnionType(obj, uncoveredtype, "value", constr, attrib=attrib)
                    unionassign.arrayelement = True
                    validvalues.append(unionassign)
                else:
                    raise self.ContextLogicError("Array elements should be type <object>", jsonobj)
            return CArrayAssign(carraytype, validvalues, attrib=attrib)
        elif isinstance(uncoveredtype, CEnumType):
            enumvalues = self.validPair(jsonobj, valpairname, expvalue=["array of strings"])
            validvalues = []
            for val in enumvalues:
                if val in uncoveredtype.values:
                    validvalues.append(val)
                else:
                    defin = self.checkIfobjectDefined(val, objtype=CEnumAssign)
                    if defin.typedef == carraytype.alias:
                        validvalues.append(val)
                    else:
                        raise self.ContextLogicError("Imcompatible ENUMERATED object '{}' assigned in array".format(val), jsonobj)
            return CArrayAssign(carraytype, validvalues, attrib=attrib)
            
        raise self.ContextLogicError("Internal error: cannot assign array type", jsonobj)
    
    '''
    This methods helps with validating if JSONPairs value and structure are as wanted
    '''
    def checkNumberConstr(self, jsonobj, ident, value, constraints):
        '''
        Checks if certain object value fulfils constraints
        :param jsonobj: jsonobject that contains value specification
        :param ident: object identifier
        :param value: object value
        :param constraints: dict of constraints
        '''
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
                    raise self.ContextLogicError("Value of '{}' ".format(ident)+\
                        "has constraint: pos-int (positive int)".format(ident), jsonobj)
        return True
    
    def checkIfobjectDefined(self, identifier, objtype=None, exception=True):
        '''
        Checks if certain object is already defined
        :param identifier: object identifier
        :param objtype: CVarType, CStructType, CUnionType or CEnumType CArrayType object
        :param exception: flag, tells if exception will be thrown when inproper type or object 
                    does not exist
        '''
        for defin in self.definitions:
            if defin.name == identifier:
                if objtype:
                    if not isinstance(defin, objtype):
                        raise self.ContextLogicError("Variable '{}' is incompatible type for assignment".format(identifier), self.currObject)
                return defin
        if exception:
            raise self.ContextLogicError("Object '{}' is not defined".format(identifier), self.currObject)
        return None
    
    def checkIftypeDeclared(self, typename, exception=True):
        '''
        Checks if certain type is already defined
        :param typename: typename that will it look for
        :param exception: flag, tells if exception will be thrown when type or type 
                    is not declared yet
        '''
        for typedef in self.declarations:
            if typedef.typename == typename:
                return typedef
        if exception:
            raise self.ContextLogicError("Type '{}' is not defined".format(typename), self.currObject)
        return None
    
    def validPair(self, jsonobj, name, expvalue=["any"], exception=True):
        '''
        Checks if pair exist in certain JSONObject object and if it holds value of given type
        :param jsonobj: JSONObject object to look for pair
        :param name: name of the pair
        :param expvalue: expected values list ("strings")
        :param exception: flag, tells if exception have to be thrown if pair does not
                exist or if it holds unsuitable type
        '''
        error = self.ContextLogicError("Missing or incorrect property" + \
                                       " '{}', expected value types {}".format(name, str(expvalue)), jsonobj)
        pair = jsonobj.getPair(name)
        if not pair:
            if exception:
                raise error
            return None
        if "string" in expvalue and pair.holdsString():
            return pair.value.string
        elif "int" in expvalue and pair.holdsNumber(numtype="int"):
            return pair.value.value
        elif "float" in expvalue and pair.holdsNumber(numtype="float"):
            return pair.value.value
        elif "object" in expvalue and pair.holdsObject():
            return pair.value
        elif "array" in expvalue and pair.holdsArray():
            return pair.value.getElements()
        elif "array of numbers" in expvalue and pair.holdsArray():
            if pair.value.holdsOnlyNumbers():
                return pair.value.getElements()
        elif "array of objects" in expvalue and pair.holdsArray():
            if pair.value.holdsOnlyObjects()():
                return pair.value.getElements()
        elif "array of strings" in expvalue and pair.holdsArray():
            if pair.value.holdsOnlyStrings():
                strings = []
                for jsonstring in pair.value.getElements():
                    strings.append(jsonstring.string)
                return strings
        elif "literal" in expvalue and pair.holdsLiteral():
            return pair.value.literal
        elif "null" in expvalue and pair.holdsLiteral():
            if pair.value.literal == "null":
                return "null"
        elif "any" in expvalue:
            return pair.value
        if exception:
            raise error
        return None
        
    def bitStringStrip(self, jsonobj, string, chunk, expectnrbits):
        '''
        Strips bit or octet string to chunks
        :param jsonobj: JSONObject that holds value (current context object)
        :param string: string to strip
        :param chunk: size of single chunk
        :param expectnrbits: expected number of bits in string to strip
        '''
        i = 0
        form = string[-1:]
        string = string[:-1]
        if form not in [ 'B', 'H' ]:
            raise self.ContextLogicError("Expected char 'B'(binary) or 'H'(hexadecimal) at the end of BIT / OCTET STRING value", jsonobj)
        hexdec = form == 'H'
        nrbits = len(string)
        if hexdec:
            nrbits = nrbits * 4
            chunk = int(chunk / 4)
        if nrbits != expectnrbits:
            raise self.ContextLogicError("Expected {} bits in BIT / OCTET STRING value".format(expectnrbits), jsonobj)
        
        prefix = "0b"
        if hexdec:
            prefix = "0x"
        bitselement = ""
        bitarray = []
        for char in string:
            i += 1
            if (not hexdec and char not in [ '0', '1' ]) or\
                 (hexdec and char not in set("0123456789abcdefABCDEF")):
                raise self.ContextLogicError("Bad value format, expected hexadecimal or binary string", jsonobj)
            bitselement += char
            if i == chunk:
                bitselement = bitselement.ljust(chunk, '0')
                bitarray.append(prefix + bitselement)
                i = 0
                bitselement = ""
        if bitselement == "":
            return bitarray
        bitselement = bitselement.ljust(chunk, '0')
        bitselement = prefix + bitselement
        bitarray.append(bitselement)
        return bitarray
    
    def ContextLogicError(self, message, jsonobj):
        return LogicError(self.currentFile, message, self.jsonFilelines[jsonobj])
    
    