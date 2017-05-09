'''
Created on 07.04.2017

@author: raqu
'''


class LexerError(Exception):
    
    def __init__(self, message, line):
        self.message = "SyntaxError: " + str(message)
        self.message += "\n>>>" + str(line)
    def __str__(self):
        return repr(self.message)


class ParserError(Exception):
    
    def __init__(self, message, line):
        self.message = "SyntaxError: " + str(message)
        self.message += "\n>>>" + str(line)
    def __str__(self):
        return repr(self.message)


class LogicError(Exception):
    
    def __init__(self, filename, message):
        self.message = "SemanticError: " + str(filename) + ": "+ str(message)
        
    def __str__(self):
        return repr(self.message)

class CSerializeError(Exception):
    
    def __init__(self, message):
        self.message = "CGenerationError: " + str(message)
        
    def __str__(self):
        return repr(self.message)



