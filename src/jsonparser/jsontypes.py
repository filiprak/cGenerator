'''
Created on 09.04.2017
JSON types such as JSONPair, JSONString, ..
They hold values of proper types
@author: raqu
'''


class JSONObject(object):
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
    def __init__(self, string=""):
        self.string = string


class JSONNumber(object):
    def __init__(self, number=0):
        self.number = number
        self.value = self.convert()
    
    def convert(self):
        # todo
        return 0
    
    def isInteger(self):
        # todo
        return True
        
class JSONLiteral(object):
    def __init__(self, literal="null"):
        self.literal = literal

