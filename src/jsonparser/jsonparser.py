'''
Created on 21.03.2017

@author: raqu
'''
from jsonparser.lexer import JSONLexer


class JSONParser():
    '''
    Main JSON jsonparser class
    '''
    def __init__(self):
        self.reader = JSONLexer()
    
    def parse(self, jsonFile):
        '''
        Parses JSON data from given file
        :param jsonFile: path to file to parse
        '''
        self.reader.loadFile(jsonFile)
        
        return None