'''
Created on 15.03.2017

@author: raqu
'''

from jsonparser.lexer import JSONLexer

def main():
    
    lexer = JSONLexer()
    name = "example.json"
    
    try:
        lexer.loadFile(name)
        res = lexer.analyze()
        for (line, type) in res:
            print(str(line) + "  " + str(type))
        
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
        
main()