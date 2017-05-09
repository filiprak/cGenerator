'''
Created on 02.05.2017

@author: raqu
'''
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from semantic_analyzer.semantic import SemanticAnalyzer
from errors import LogicError
from jsonparser.jsontypes import JSONObject, JSONPair, JSONArray, JSONString



analyzer = SemanticAnalyzer()

testcase = dict()

a = JSONObject()
a.append(JSONPair("moduleName", JSONString("A")))
imp = JSONArray()
imp.insert(JSONString("C"))
a.append(JSONPair("imports", imp))

b = JSONObject()
b.append(JSONPair("moduleName", JSONString("B")))
imp = JSONArray()
imp.insert(JSONString("C"))
b.append(JSONPair("imports", imp))

c = JSONObject()
c.append(JSONPair("moduleName", JSONString("C")))
imp = JSONArray()
#imp.insert(JSONString("A"))
#c.append(JSONPair("imports", imp))

testcase["a.json"] = a
testcase["b.json"] = b
testcase["c.json"] = c

try:
    analyzer.parsedDict = testcase
    print analyzer.dependencySort(testcase)
except LogicError as e:
    print e.message





