'''
Created on 16.04.2017
Script tests if parser works correctly
@author: raqu
'''

from jsonparser.lexer import JSONLexer
from errors import LexerError, ParserError
from jsonparser.jsonparser import JSONParser
from jsonparser.jsontypes import JSONObject, JSONPair, JSONString, JSONNumber,\
    JSONArray


# debuging purposes
import sys
from jsonparser.constants import Token

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


def testParser():
    tcase1file = "testcases/testcase01.json"
    tcase2file = "testcases/testcase02.json"
    
    lexer = JSONLexer()
    parser = JSONParser()
    
    try:
        """test case 1"""
        
        print("Testing parser: {}".format(tcase1file))
        
        lexer.loadFile(tcase1file)
        tokenized = lexer.analyze()
        
        """for (l, t, s) in tokenized:
            print("{:>6} {:>20} {:>20}".format(l, Token.toString(t), s))"""
        
        parsed = parser.parse(tokenized, tcase1file)
        
        
        
        testcase01 = TestCase01()
        
        if testcase01.isTheSameAs(parsed):
            print("Testcase 01: TEST PASSED")
        else:
            print("Testcase 01: TEST FAILED")
            
        
        """test case 2"""
        
        print("Testing parser: {}".format(tcase2file))
        
        lexer.loadFile(tcase2file)
        tokenized = lexer.analyze()
        
        parsed = parser.parse(tokenized, tcase2file)
        
        testcase02 = TestCase02()
        
        if testcase02.isTheSameAs(parsed):
            print("Testcase 02: TEST PASSED")
        else:
            print("Testcase 02: TEST FAILED")
    
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
    except LexerError as leErr:
        print(leErr.message)
        print("Testing: testcase01: lexer failed")
    except ParserError as paErr:
        print(paErr.message)
        print("Testing: testcase01: parser failed")
    

class TestCase01(object):
    def __init__(self):
        parsed = JSONObject()
        parsed.append(JSONPair("moduleName", JSONString("Math")))
        
        attributex = JSONObject()
        attributex.append(JSONPair("attribute", JSONString("x")))
        attributex.append(JSONPair("type", JSONString("REAL")))
        attributex.append(JSONPair("max", JSONNumber("10.0")))
        attributex.append(JSONPair("min", JSONNumber("-10.0")))
        
        attributey = JSONObject()
        attributey.append(JSONPair("attribute", JSONString("y")))
        attributey.append(JSONPair("type", JSONString("REAL")))
        
        attributez = JSONObject()
        attributez.append(JSONPair("attribute", JSONString("z")))
        attributez.append(JSONPair("type", JSONString("REAL")))
        
        attrarray = JSONArray()
        attrarray.insert(attributex)
        attrarray.insert(attributey)
        attrarray.insert(attributez)
        
        typeVector = JSONObject()
        typeVector.append(JSONPair("typeName", JSONString("Vector")))
        typeVector.append(JSONPair("type", JSONString("SEQUENCE")))
        typeVector.append(JSONPair("contents", attrarray))
        
        objectmyvect = JSONObject()
        objectmyvect.append(JSONPair("objectName", JSONString("myvect")))
        objectmyvect.append(JSONPair("type", JSONString("Vector")))
        
        valueobj = JSONObject()
        valueobj.append(JSONPair("x", JSONNumber("3.0")))
        valueobj.append(JSONPair("y", JSONNumber("5.3")))
        valueobj.append(JSONPair("z", JSONNumber("-3.7")))

        objectmyvect.append(JSONPair("value", valueobj))

        modulearray = JSONArray()
        modulearray.insert(typeVector)
        modulearray.insert(objectmyvect)
        
        parsed.append(JSONPair("moduleContent", modulearray))
        self.parsed = parsed
    
    def isTheSameAs(self, jsontype):
        return jsontype.equals(self.parsed)


class TestCase02(object):
    def __init__(self):
        parsed = JSONObject()
        parsed.append(JSONPair("moduleName", JSONString("Plane")))
        
        importsarray = JSONArray()
        importsarray.insert(JSONString("Math"))
        parsed.append(JSONPair("imports", importsarray))
        
        attributex = JSONObject()
        attributex.append(JSONPair("attribute", JSONString("normal")))
        attributex.append(JSONPair("type", JSONString("Vector")))
        
        attributey = JSONObject()
        attributey.append(JSONPair("attribute", JSONString("area")))
        attributey.append(JSONPair("type", JSONString("REAL")))
        attributey.append(JSONPair("encoding", JSONString("IEEE754-1985-32")))
        
        attributez = JSONObject()
        attributez.append(JSONPair("attribute", JSONString("name")))
        attributez.append(JSONPair("type", JSONString("CHARACTER STRING")))
        attributez.append(JSONPair("size", JSONNumber("32")))
        
        attrarray = JSONArray()
        attrarray.insert(attributex)
        attrarray.insert(attributey)
        attrarray.insert(attributez)
        
        typeVector = JSONObject()
        typeVector.append(JSONPair("typeName", JSONString("Plane")))
        typeVector.append(JSONPair("type", JSONString("SET")))
        typeVector.append(JSONPair("contents", attrarray))
        
        objectmyvect = JSONObject()
        objectmyvect.append(JSONPair("objectName", JSONString("norm")))
        objectmyvect.append(JSONPair("type", JSONString("Vector")))
        
        valueobj = JSONObject()
        valueobj.append(JSONPair("x", JSONNumber("1.0")))
        valueobj.append(JSONPair("y", JSONNumber("0.0")))
        valueobj.append(JSONPair("z", JSONNumber("0.0")))
        
        objectmyvect.append(JSONPair("value", valueobj))

        objectmyplane = JSONObject()
        objectmyplane.append(JSONPair("objectName", JSONString("plane")))
        objectmyplane.append(JSONPair("type", JSONString("Plane")))
        
        valueobjp = JSONObject()
        valueobjp.append(JSONPair("normal", JSONString("norm")))
        valueobjp.append(JSONPair("area", JSONNumber("30.0")))
        valueobjp.append(JSONPair("name", JSONString("plane-01")))
        
        objectmyplane.append(JSONPair("value", valueobjp))
        
        modulearray = JSONArray()
        modulearray.insert(typeVector)
        modulearray.insert(objectmyvect)
        modulearray.insert(objectmyplane)
        
        parsed.append(JSONPair("moduleContent", modulearray))
        self.parsed = parsed
    
    def isTheSameAs(self, jsontype):
        return jsontype.equals(self.parsed)


"""run parser test"""
testParser()



    