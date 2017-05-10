'''
Created on 10.05.2017

@author: raqu
'''
from errors import LogicError


class DefinitionResolver():
    def __init__(self, declarations, defines):
        self.declarations = declarations
        self.defines = defines
        self.jsonFilelines = None
        self.currentFile = None
        self.currObject = None
        
    def resolve(self, filename, jsonobj, jsonFilelines):
        # setup context
        self.currentFile = filename
        self.jsonFilelines = jsonFilelines
        self.currObject = jsonobj
        
        return
        
    def ContextLogicError(self, message):
        return LogicError(self.currentFile, message, self.jsonFilelines[self.currObject])