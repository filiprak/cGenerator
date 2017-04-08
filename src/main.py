'''
Created on 15.03.2017

@author: raqu
'''

from jsonparser.lexer import JSONLexer
from errors import LexerError

def main():
    
    lexer = JSONLexer()
    name = "example.json"
    
    try:
        lexer.loadFile(name)
        res = lexer.analyze()
        for (line, type, string) in res:
            print(str(line) + "  " + str(type) + "  " + str(string))
        
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
    except LexerError as leErr:
        print(leErr.message)
        
main()