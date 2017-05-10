'''
Created on 10.05.2017
Module contains C object assign variables representations in python
Objects have method str() overriden so they can be serialized to
text form by calling str(object). Text form is gramatically valid
for C language (in C99 standard).
@author: raqu
'''
from errors import CSerializeError
from ctypes import CArrayType, CStructType, CEnumType, CUnionType,\
    CVarType, indent


class CVarAssign():
    '''
    Represents variable assign C code snippet.
    Can only be simple type, not structured.
    '''
    def __init__(self, vartype, value, attrib=False):
        '''
        :param vartype: CVarType variable type
        :param value: represents value of variable
        :param attrib: should be set 'True' if variable is part of structured type
        '''
        self.vartype = vartype
        self.value = value
        self.attrib = attrib
    
    def __str__(self):
        if self.attrib:
            return ".{} = {}".format(str(self.vartype.name),
                                     str(self.value))
        return "{} {} = {};".format(str(self.vartype.variabletype),
                                    str(self.vartype.name),
                                    str(self.value))

 
class EnumAssign():
    '''
    Represents enum variable assignment C code snippet
    '''
    def __init__(self, enumtype, name, value, semicol=True, attrib=False):
        '''
        :param enumtype: CEnumType object
        :param name: variable identifier
        :param value: assigned value (string format)
        '''
        self.enumtype = enumtype
        self.name = name
        self.value = value
        self.attrib = attrib
        self.semicol = semicol
    
    def __str__(self):
        string = "enum "
        if self.enumtype.enumname != None:
            string += self.enumtype.enumname + " "
        if self.attrib:
            string = "."
        string += "{} = {}".format(str(self.name),
                                        str(self.value))
        if self.semicol:
            string += ";"
        return string
    
    
class CStructAssign():
    '''
    Represents struct variable assign C code snippet
    '''
    def __init__(self, structtype, name, values, typedef=None, semicol=True, attrib=False):
        '''
        :param structtype: CStructType object
        :param name: variable identifier
        :param values: dict of attributes values
        :param typedef: type name that covers struct type (string format)
        '''
        self.structtype = structtype
        self.name = name
        self.typedef = typedef
        self.semicol = semicol
        self.values = values
        self.attrib = attrib
        self.assigned = None

    def __str__(self):
        strAttributes = "{"
        #last element indicator
        last = self.structtype.attributes[len(self.structtype.attributes) - 1]
        for a in self.structtype.attributes:
            if not isinstance(a, (CVarType, CArrayType)):
                raise CSerializeError("Illegal struct member in: " + self.uniontype.unionname)
            if a.name not in self.values:
                raise CSerializeError("Struct attribute left unassigned: " + self.uniontype.unionname + ": " + a.name)
            if isinstance(a, CVarType):
                if isinstance(a.variabletype, CStructType):
                    self.assigned = CStructAssign(a.variabletype, a.name, self.values[a.name], semicol=False, attrib=True)
                elif isinstance(a.variabletype, CEnumType):
                    self.assigned = CVarAssign(a.variabletype, self.values[a.name], attrib=True)
                elif isinstance(a.variabletype, CUnionType):
                    self.assigned = CUnionAssign(a.variabletype, a.name, self.values[a.name], semicol=False, attrib=True)
                else:
                    self.assigned = CVarAssign(a, self.values[a.name], attrib=True)
            elif isinstance(a, CArrayType):
                self.assigned = CArrayAssign(a, self.values[a.name], semicol=False, attrib=True)

            attr = indent(str(self.assigned))
            strAttributes += "\n{}".format(attr)
            if a != last:
                strAttributes += ","
        strAttributes += "\n}"
        
        string = "struct "
        if self.structtype.structname != None:
            string =+ str(self.structtype.structname) + " "
        if self.typedef != None:
            string = self.typedef + " "
        if self.attrib:
            string = "."
        string += "{} = {}".format(str(self.name), str(strAttributes))
        if self.semicol:
            string += ";"
        return string
    
    
class CUnionAssign():
    '''
    Represents union variable assign C code snippet
    '''
    def __init__(self, uniontype, name, value, typedef=None, semicol=True, attrib=False):
        '''
        :param uniontype: CUnionType object
        :param name: variable identifier
        :param value: dict of one value to assign
        :param typedef: type name that covers union type (string format)
        '''
        self.uniontype = uniontype
        self.name = name
        self.value = value
        self.typedef = typedef
        self.semicol = semicol
        self.attrib = attrib
        self.assigned = None

    def __str__(self):
        strAttributes = "{"
        for a in self.uniontype.attributes:
            if not isinstance(a, (CVarType, CArrayType)):
                raise CSerializeError("Illegal union member in: " + self.uniontype.unionname)
            if a.name in self.value.keys():
                if isinstance(a, CVarType):
                    if isinstance(a.variabletype, CStructType):
                        self.assigned = CStructAssign(a.variabletype, a.name, self.value[a.name], semicol=False, attrib=True)
                    elif isinstance(a.variabletype, CEnumType):
                        self.assigned = CVarAssign(a.variabletype, self.value[a.name], attrib=True)
                    elif isinstance(a.variabletype, CUnionType):
                        self.assigned = CUnionAssign(a.variabletype, a.name, self.value[a.name], semicol=False, attrib=True)
                    else:
                        self.assigned = CVarAssign(a, self.value[a.name], attrib=True)
                elif isinstance(a, CArrayType):
                    self.assigned = CArrayAssign(a, self.value[a.name], semicol=False, attrib=True)
                break
        if self.assigned == None:
            raise CSerializeError("Illegal union assignment value: " + self.uniontype.unionname)
            
        strAttributes += "\n{}\n".format(indent(str(self.assigned)))
        strAttributes += "}"

        string = "union "
        if self.uniontype.unionname != None:
            string += self.uniontype.unionname + " "
        if self.typedef != None:
            string = self.typedef + " "
        if self.attrib:
            string = "."
        
        string += "{} = {}".format(str(self.name),
                                      str(strAttributes))
        if self.semicol:
            string += ";"
        return string


class CArrayAssign():
    '''
    Represents array initialization C code snippet
    '''
    def __init__(self, arrtype, values, attrib=False, semicol=False):
        '''
        :param arrtype: CArrayType object
        :param values: list of elements
        '''
        self.arrtype = arrtype
        self.values = values
        self.attrib = attrib
        self.semicol = semicol
    
    def __str__(self):
        strValues = "{"
        strValues += " {}".format(str(self.values[0]))
        for v in self.values[1:]:
            strValues += ", {}".format(str(v))
        strValues +=" }"
        
        if self.attrib:
            return ".{} = {}".format(str(self.arrtype.name),
                                     str(strValues))
        string = "{} {}[{}] = {};".format(str(self.arrtype.valtype),
                                        str(self.arrtype.name),
                                        str(self.arrtype.size),
                                        str(strValues))
        if self.semicol:
            string += ";"
        return string
    
    
    
    