'''
Created on 21.03.2017
Test functions
@author: raqu
'''

from jsonparser.lexer import JSONLexer
from errors import LexerError


def testLexerRead(withWhSpaces, trace=False):
    '''
    Unit test for JSONLexer.read() function
    :param withWhSpaces: with or without whitespaces taking into account
    :param trace: tells if detailed output have to be printed
    '''
    
    print("Testing JSONLexer.read(): whitespaces: " + str(withWhSpaces))
    
    lexer = JSONLexer()
    name = "example.json"
    
    try:
        lexer.loadFile(name)
        
        currCharact = lexer.read(whitespaces=withWhSpaces)
        nextCharact = lexer.nextChar
        errors = 0
        while currCharact:
            if trace:
                print("line: {}, current: [{}], next: [{}]".format(lexer.currentLine,
                                                              lexer.lastChar,
                                                              lexer.nextChar))
            currCharact = lexer.read(whitespaces=withWhSpaces)
            
            if nextCharact != currCharact:
                errors += 1
                print("error: [{}] != [{}]".format(currCharact, nextCharact))
            
            nextCharact = lexer.nextChar
        
        print("TEST RESULTS: errors: {}".format(errors))
        
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
    except LexerError as leErr:
        print(leErr.message)
    
        
"""run tests JSONLexer.read()"""
testLexerRead(True, trace=True)
testLexerRead(False)


