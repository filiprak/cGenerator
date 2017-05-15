'''
Created on 07.04.2017
Module of exceptions declaration
@author: raqu
'''

class Format():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LexerError(Exception):
    
    def __init__(self, message, line):
        self.message = Format.FAIL + Format.BOLD + "SyntaxError: " + str(message) + Format.ENDC + Format.ENDC
        self.message += "\n>>>" + Format.OKBLUE + str(line) + Format.ENDC
    def __str__(self):
        return repr(self.message)


class ParserError(Exception):
    
    def __init__(self, message, line):
        self.message = Format.FAIL + Format.BOLD + "SyntaxError: " + str(message) + Format.ENDC + Format.ENDC
    def __str__(self):
        return repr(self.message)


class LogicError(Exception):
    
    def __init__(self, filename, message, line):
        self.message = Format.FAIL + Format.BOLD + "SemanticError: " + \
            str(filename) + ": line:" + str(line)+ ": " + str(message) + Format.ENDC + Format.ENDC
        
    def __str__(self):
        return repr(self.message)

class CSerializeError(Exception):
    
    def __init__(self, message):
        self.message = Format.FAIL + Format.BOLD + "CGenerationError: " + str(message) + Format.ENDC + Format.ENDC
        
    def __str__(self):
        return repr(self.message)



