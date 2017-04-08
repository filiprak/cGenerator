'''
Created on 21.03.2017
JSON files parser
@author: raqu
'''


from jsonparser.lexer import JSONLexer


class JSONParser():
    '''
    Main JSON jsonparser class
    '''
    def __init__(self):
        self.lexer = JSONLexer()
    
    def parse(self, jsonFile):
        '''
        Parses JSON data from given file
        :param jsonFile: path to file to parse
        '''
        self.lexer.loadFile(jsonFile)
        
        return None