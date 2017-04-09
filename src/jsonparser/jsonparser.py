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
        self.tokenTable = None
    
    def parse(self, input):
        '''
        Parses JSON data from given file
        :param jsonFile: path to file to parse
        '''
        if input == None:
            return None
        
        return None
    
    def parseJSONObject(self):
        return None