'''
Created on 04.05.2017
Module contains C object types classes representations in python
Objects have method str() overriden
@author: raqu
'''
from errors import CSerializeError

def indent(string, nrtabs=1):
    padding = ""
    for i in range(nrtabs):
        padding += "\t"
    return padding + ('\n'+ padding).join(string.rstrip().split('\n'))


class CPreprocConstDefine():
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return "#define {}/t{}".format(str(self.name), str(self.value))
        

class CVarType():
    def __init__(self, variabletype, name):
        self.variabletype = variabletype
        if not isinstance(variabletype, str):
            self.variabletype.semicol = False
        self.name = name
    
    def __str__(self):
        return "{} {};".format(str(self.variabletype),
                               str(self.name))

class CVarAssign():
    def __init__(self, vartype, value, attrib=False):
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
    
class CTypedef():
    def __init__(self, covered, typename):
        self.covered = covered
        if not isinstance(covered, str):
            self.covered.semicol = False
        self.typename = typename

    def __str__(self):
        return "typedef {} {};".format(str(self.covered), str(self.typename))

class CEnumType():
    def __init__(self, name, values, semicol=True):
        self.name = name
        self.values = values
        self.semicol = semicol

    def __str__(self):
        strValues = "{"
        strValues += " {}".format(self.values[0])
        for v in self.values[1:]:
            strValues += ", {}".format(v)
        strValues += " }"
        
        string = "enum {} {}".format(str(self.name),
                                   str(strValues))
        if self.semicol:
            string += ";"
        return string

class EnumAssign():
    def __init__(self, enumtype, name, value, semicol=True):
        self.enumtype = enumtype
        self.name = name
        self.value = value
        self.semicol = semicol
    
    def __str__(self):
        string = "enum {} {} = {}".format(str(self.enumtype.name),
                                         str(self.name),
                                         str(self.value))
        if self.semicol:
            string += ";"
        return string

class CStructType():
    def __init__(self, structname, attributes=[], semicol=True):
        self.structname = structname
        self.attributes = attributes
        self.semicol = semicol

    def __str__(self):
        strAttributes = "{"
        for a in self.attributes:
            attr = indent(str(a))
            strAttributes += "\n{}".format(attr)
        strAttributes += "\n}"
        string = "struct {} {}".format(str(self.structname),
                                      str(strAttributes))
        if self.semicol:
            string += ";"
        return string

class CStructAssign():
    def __init__(self, structtype, name, values, typedef=None, semicol=True, attrib=False):
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
        
        string = "struct " + str(self.structtype.structname) + " "
        if self.typedef != None:
            string = self.typedef + " "
        if self.attrib:
            string = "."
        string += "{} = {}".format(str(self.name), str(strAttributes))
        if self.semicol:
            string += ";"
        return string

class CUnionType():
    def __init__(self, unionname, attributes=[], semicol=True):
        self.unionname = unionname
        self.attributes = attributes
        self.semicol = semicol

    def __str__(self):
        strAttributes = "{"
        for a in self.attributes:
            attr = indent(str(a))
            strAttributes += "\n{}".format(attr)
        strAttributes += "\n}"
        string = "union {} {}".format(str(self.unionname),
                                      str(strAttributes))
        if self.semicol:
            string += ";"
        return string

class CUnionAssign():
    def __init__(self, uniontype, name, value, typedef=None, semicol=True, attrib=False):
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

        string = "union " + self.uniontype.unionname + " "
        if self.typedef != None:
            string = self.typedef + " "
        if self.attrib:
            string = "."
        
        string += "{} = {}".format(str(self.name),
                                      str(strAttributes))
        if self.semicol:
            string += ";"
        return string
    
class CArrayType():
    def __init__(self, valtype, name, size):
        self.valtype = valtype
        self.name = name
        self.size = size
    
    def __str__(self):
        return "{} {}[{}];".format(str(self.valtype), str(self.name), str(self.size))

class CArrayAssign():
    def __init__(self, arrtype, values, attrib=False, semicol=False):
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





"""testing -------------------------------------------------------------------------------"""

vart = CVarType("int", "number")
var = CVarAssign(vart, 4e55)

array = CArrayType("char", "arrayname", 3)
arrAssign = CArrayAssign(array, [ 1,3,4])

enumt = CEnumType("Position", [ "UP", "DOWN", "LEFT"  ])

structt1 = CStructType("Mysss", [array, array, vart])

uniont = CUnionType("MYunion", [vart, array, ])

vart1 = CVarType(structt1, "s1")
structt = CStructType("Mysss", [array, vart])

varstruct = CVarType(structt, "mystruct")

uniont = CUnionType("MYunion", [vart, array, varstruct])

value = dict()
structvalue = dict()
structvalue["arrayname"] = [ "\"sss\"", "asf", "abcdef"]
structvalue["number"] = 333
value["mystruct"] = structvalue

uniontypedef = CTypedef(uniont, "UnionType")
uniona = CUnionAssign(uniont, "instance", value, typedef="UnionType")


print(str(varstruct))

print(str(uniontypedef))
print(str(uniona))

        