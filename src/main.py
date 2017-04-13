'''
Created on 15.03.2017
Main module contains main() function
@author: raqu
'''

from jsonparser.lexer import JSONLexer
from errors import LexerError, ParserError
from jsonparser.jsonparser import JSONParser
from jsonparser.constants import Token


def main():
    '''
    Main program function
    '''
    
    lexer = JSONLexer()
    parser = JSONParser()
    name = "example.json"
    
    try:
        lexer.loadFile(name)
        res = lexer.analyze()
        
        
        for (l, t, s) in res:
            print("{:>6} {:>20} {:>20}".format(l, Token.toString(t), s))
        parsed = parser.parse(res, name)
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
    except LexerError as leErr:
        print(leErr.message)
    except ParserError as paErr:
        print(paErr.message)


"""start program execution"""
main()