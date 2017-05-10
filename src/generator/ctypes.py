'''
Created on 04.05.2017
Module contains C object types classes representations in python
Objects have method str() overriden so they can be serialized to
text form by calling str(object). Text form is gramatically valid
for C language (in C99 standard).
@author: raqu
'''


# helper func for indenting multiline string
def indent(string, nrtabs=1):
    padding = ""
    for i in range(nrtabs):
        padding += "\t"
    return padding + ('\n'+ padding).join(string.rstrip().split('\n'))


class CPreprocConstDefine():
    '''
    Represents C preprocessor define: #define name value
    '''
    def __init__(self, name, value):
        self.name = name
        self.value = value
    
    def __str__(self):
        return "#define {}\t{}".format(str(self.name), str(self.value))
        

class CVarType():
    '''
    Represents declaration of C variable
    Can be simple or structured type 
    '''
    def __init__(self, variabletype, name, constraints=dict()):
        self.variabletype = variabletype
        if not isinstance(variabletype, str):
            self.variabletype.semicol = False
        self.name = name
        self.constraints = constraints
    
    def __str__(self):
        return "{} {};".format(str(self.variabletype),
                               str(self.name))


    
class CTypedef():
    '''
    Representation of C typedef code snippet
    Can be used for structured and simple types
    '''
    def __init__(self, covered, typename, constraints=dict()):
        '''
        :param covered: covered type (structural(object) or simple - string)
        :param typename: name of new type
        '''
        self.covered = covered
        if not isinstance(covered, str):
            self.covered.semicol = False
        self.typename = typename
        self.constraints = constraints
        
    def __str__(self):
        return "typedef {} {};".format(str(self.covered), str(self.typename))

class CEnumType():
    '''
    Represents enum declaration C code snippet
    '''
    def __init__(self, values, enumname=None,  semicol=True):
        '''
        :param enumname: enum <enumname> { ...
        :param values: list of string values that will be enumerated
        :param semicol: flag, if ";" should be put at the end then 'True'
        '''
        self.enumname = enumname
        self.values = values
        self.semicol = semicol

    def __str__(self):
        strValues = "{"
        strValues += " {}".format(self.values[0])
        for v in self.values[1:]:
            strValues += ", {}".format(v)
        strValues += " }"
        
        string = "enum "
        if self.enumname != None:
            string += self.enumname + " "
        string += str(strValues)
        if self.semicol:
            string += ";"
        return string





class CStructType():
    '''
    Represents struct type declaration C code snippet
    '''
    def __init__(self, attributes=[], structname=None, semicol=True):
        '''
        :param structname: name of struct type 'struct <structname> {...'
        :param attributes: list of struct attributes (C*Type objects)
        '''
        self.structname = structname
        self.attributes = attributes
        self.semicol = semicol

    def __str__(self):
        strAttributes = "{"
        for a in self.attributes:
            attr = indent(str(a))
            strAttributes += "\n{}".format(attr)
        strAttributes += "\n}"
        string = "struct "
        if self.structname != None:
            string += self.structname + " "
        string += str(strAttributes)
        if self.semicol:
            string += ";"
        return string


class CUnionType():
    '''
    Represents union type declaration C code snippet
    '''
    def __init__(self, attributes=[], unionname=None, semicol=True):
        '''
        :param unionname: name of union type 'union <unionname> {...'
        :param attributes: list of union attributes (C*Type objects)
        '''
        self.unionname = unionname
        self.attributes = attributes
        self.semicol = semicol

    def __str__(self):
        strAttributes = "{"
        for a in self.attributes:
            attr = indent(str(a))
            strAttributes += "\n{}".format(attr)
        strAttributes += "\n}"
        string = "union "
        if self.unionname != None:
            string += self.unionname + " "
        string += str(strAttributes)
        if self.semicol:
            string += ";"
        return string

  
class CArrayType():
    '''
    Represents array declaration C code snippet
    '''
    def __init__(self, valtype, name, size):
        '''
        :param valtype: type of elements
        :param name: array identifier
        :param size: array size
        '''
        self.valtype = valtype
        if not isinstance(valtype, str):
            valtype.semicol = False
        self.name = name
        self.size = size
    
    def __str__(self):
        return "{} {}[{}];".format(str(self.valtype), str(self.name), str(self.size))



"""testing -------------------------------------------------------------------------------

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
"""
        