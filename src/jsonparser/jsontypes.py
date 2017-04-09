'''
Created on 09.04.2017
JSON types such as JSONPair, JSONString, ..
They hold values of proper json types
@author: raqu
'''


class JSONObject(object):
    '''
    Represents json object, pairs can be add using append method
    '''
    def __init__(self):
        self.pairs = []
    
    def append(self, pair):
        if pair == None:
            return
        self.pairs.append(pair)
    
    def getPairNames(self):
        names = []
        for pair in self.pairs:
            names.append(pair.name)
        
        
class JSONPair(object):
    '''
    Represents json pair, name is string name of pair,
    value is one of: JSONObject, JSONNumber, JSONString, JSONArray, JSONLiteral
    '''
    def __init__(self, name="", value=None):
        self.name = name
        self.value = value
    
    def holdsNumber(self):
        return self.value.__class__ == JSONNumber().__class__
    
    def holdsString(self):
        return self.value.__class__ == JSONString().__class__
    
    def holdsArray(self):
        return self.value.__class__ == JSONArray().__class__
    
    def holdsObject(self):
        return self.value.__class__ == JSONObject().__class__
    
    def holdsLiteral(self):
        return self.value.__class__ == JSONLiteral().__class__


class JSONArray(object):
    '''
    Represents json array, can hold same values as json pair
    '''
    def __init__(self):
        self.elements = dict()
        self.size = 0
        
    def insert(self, element):
        self.elements[self.size] = element
        self.size += 1
        
    def getElement(self, index):
        if index == None:
            return None
        if index >= self.size:
            return None
        return self.elements[index]
    
    def holdsNumber(self, index):
        return self.getElement(index).__class__ == JSONNumber().__class__
    
    def holdsString(self, index):
        return self.getElement(index).__class__ == JSONString().__class__
    
    def holdsArray(self, index):
        return self.getElement(index).__class__ == JSONArray().__class__
    
    def holdsObject(self, index):
        return self.getElement(index).__class__ == JSONObject().__class__
    
    def holdsLiteral(self, index):
        return self.getElement(index).__class__ == JSONLiteral().__class__


class JSONString(object):
    '''
    Represents json character string
    '''
    def __init__(self, string=""):
        self.string = string

    def matches(self, string):
        if string == None:
            return False
        return self.string == string

class JSONNumber(object):
    '''
    Represents json number, can be float, integer, positive or negative number
    value is converted from given string number representation to float value
    value is interpreted as integer when it fraction part equals 0
    '''
    def __init__(self, number=""):
        self.number = number
        self.value = float(number)
    
    def isInteger(self):
        return float(self.number) == int(float(self.number))
    
    def isFloat(self):
        return not self.isInteger()
    
    def getValue(self):
        return self.value
    
    
class JSONLiteral(object):
    '''
    Represents json null, true or false values
    '''
    def __init__(self, literal="null"):
        self.literal = literal

    def isTrue(self):
        return self.literal == "true"

    def isNull(self):
        return self.literal == "null"

    def isFalse(self):
        return self.literal == "false"

