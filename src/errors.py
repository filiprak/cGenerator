'''
Created on 07.04.2017

@author: raqu
'''


class LexerError(Exception):
    
    def __init__(self, message):
        self.message = "SyntaxError: " + str(message)
        
    def __str__(self):
        return repr(self.message)


class ParserError(Exception):
    
    def __init__(self, message):
        self.message = "ParseError: " + str(message)
        
    def __str__(self):
        return repr(self.message)


class LogicError(Exception):
    
    def __init__(self, message):
        self.message = "SemanticError: " + str(message)
        
    def __str__(self):
        return repr(self.message)




