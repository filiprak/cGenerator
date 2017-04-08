'''
Created on 15.03.2017

@author: raqu
'''

from jsonparser.lexer import JSONLexer
from errors import LexerError
from jsonparser.constants import Token

def main():
    
    lexer = JSONLexer()
    name = "example.json"
    
    try:
        lexer.loadFile(name)
        res = lexer.analyze()
        for (line, ttype, string) in res:
            print("{:>5} {:<15} {:<20}".format(line, Token.toString(ttype), string))
        
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
    except LexerError as leErr:
        print(leErr.message)
        
main()