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
        return names
    
    def getPairValue(self, name):
        for pair in self.pairs:
            if pair.name == name:
                return pair.value
        return None
    
    def getPair(self, name):
        for pair in self.pairs:
            if pair.name == name:
                return pair
        return None
    
    def empty(self):
        return len(self.pairs) == 0
    
    def hasPair(self, jsonpair):
        if jsonpair == None:
            return False
        for pair in self.pairs:
            if pair.equals(jsonpair):
                return True
        return False
    
    def equals(self, jsonobject):
        if self.empty() and not jsonobject.empty():
            return False
        if not self.empty() and jsonobject.empty():
            return False
        if len(self.pairs) != len(jsonobject.pairs):
            return False
        for pair in self.pairs:
            if not jsonobject.hasPair(pair):
                return False
        return True
            
        
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
    
    def equals(self, jsonpair):
        return self.name == jsonpair.name and self.value.equals(jsonpair.value)


class JSONArray(object):
    '''
    Represents json array, can hold same values as json pair
    '''
    def __init__(self):
        self.elements = dict()
        self.size = 0
    
    def empty(self):
        return self.size == 0
    
    def insert(self, element):
        self.elements[self.size] = element
        self.size += 1
        
    def getElement(self, index):
        if index == None:
            return None
        if index >= self.size:
            return None
        return self.elements[index]
    
    def getElements(self):
        return self.elements.values()
    
    def holdsNumber(self, index):
        return self.getElement(index).__class__ == JSONNumber().__class__
    
    def holdsString(self, index):
        return self.getElement(index).__class__ == JSONString().__class__
    
    def holdsOnlyStrings(self):
        for element in self.elements.values():
            if element.__class__ != JSONString().__class__:
                return False
        return True
    
    def holdsArray(self, index):
        return self.getElement(index).__class__ == JSONArray().__class__
    
    def holdsObject(self, index):
        return self.getElement(index).__class__ == JSONObject().__class__
    
    def holdsOnlyObjects(self):
        for element in self.elements.values():
            if element.__class__ != JSONObject().__class__:
                return False
        return True
    
    def holdsLiteral(self, index):
        return self.getElement(index).__class__ == JSONLiteral().__class__

    def equals(self, jsonarray):
        if self.size != jsonarray.size:
            return False
        for i in range(self.size):
            if not self.elements[i].equals(jsonarray.elements[i]):
                return False
        return True


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

    def equals(self, jsonstring):
        return self.string == jsonstring.string
    
    
class JSONNumber(object):
    '''
    Represents json number, can be float, integer, positive or negative number
    value is converted from given string number representation to float value
    value is interpreted as integer when it doesn't contain '.' or 'e'/'E' chars in string
    '''
    def __init__(self, number="0"):
        self.number = number
        self.numtype = None
        self.value = self.calcNumber()
    
    def calcNumber(self):
        if '.' in self.number or 'e' in self.number or 'E' in self.number:
            self.numtype = "float"
            return float(self.number)
        self.numtype = "int"
        return int(self.number)
    
    def isInteger(self):
        return self.numtype == "int"
    
    def isFloat(self):
        return self.numtype == "float"
    
    def getValue(self):
        return self.value
    
    def equals(self, jsonnum):
        return self.value == jsonnum.value
    
    
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

    def equals(self, jsonliter):
        return self.literal == jsonliter.literal
    
    
