'''
Created on 16.04.2017
Script prints output tokens from lexer analize
@author: raqu
'''
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from jsonparser.lexer import JSONLexer


# debuging purposes
import sys
from jsonparser.constants import Token
from errors import LexerError

def tracefunc(frame, event, arg, indent=[0]):
    substring_list = ["parse", "equals"]
    if not any(substring in frame.f_code.co_name for substring in substring_list):
        return tracefunc
    
    if event == "call":
        indent[0] += 1
        print "| " * indent[0], "call function", frame.f_code.co_name
    elif event == "return":
        #print "| " * indent[0], "exit function", frame.f_code.co_name
        indent[0] -= 1
    return tracefunc


#sys.settrace(tracefunc)


def testLexer(testcase):
  
    lexer = JSONLexer()
    
    try:
        """test case 1"""
        
        print("Testing lexer: {}".format(testcase))
        
        lexer.loadFile(testcase)
        tokenized = lexer.analyze()
        
        for (l, t, s) in tokenized:
            print("{:>6} {:>20} {:>20}".format(l, Token.toString(t), s))        
    
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
    except LexerError as leErr:
        print(leErr.message)
        print("Testing: testcase01: lexer failed")
        
   
tcase1file = "testcases/testcase01.json"
tcase2file = "testcases/testcase02.json"
   
"""run lexer test"""
testLexer(tcase1file)



    