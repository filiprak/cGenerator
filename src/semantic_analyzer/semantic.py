'''
Created on 28.04.2017
Semantic analyzer main module,
contains functions of semantic actions over parsed file
@author: raqu
'''
from errors import LogicError

def isJSONObject(obj):
    return 

class SemanticAnalyzer():
    def __init__(self):
        self.parsedDict = None
        self.processOrder = None
        
    def analyze(self, parsedDict=dict()):
        if len(parsedDict.keys()) == 0:
            return None
        self.parsedDict = parsedDict
        self.processOrder = self.dependencySort(parsedDict)
    
    def dependencySort(self, parsedDict):        
        for filename in parsedDict.keys():
            parsed = parsedDict[filename]
            modulenamePair = parsed.getPair("moduleName")
            if not modulenamePair:
                raise LogicError(filename, "Module name tag required: \"moduleName\":<name>")
            if not modulenamePair.holdsString():
                raise LogicError(filename, "Incorrect value, should be string value\"moduleName\":<string>")
            importsPair = parsed.getPair("imports")
            if importsPair:
                if not importsPair.holdsArray():
                    raise LogicError(filename, "Incorrect imports value\"imports\":[ names ]")
                if not importsPair.value.holdsOnlyStrings():
                    raise LogicError(filename, "Incorrect imports value\"imports\":[ \"module1\", \"module2\", ...  ]")

        modulesDict = dict()
        for filename in parsedDict.keys():
            parsed = parsedDict[filename]
            modulenamePair = parsed.getPair("moduleName")
            importsPair = parsed.getPair("imports")
            if modulenamePair in modulesDict.keys():
                raise LogicError(filename, "Duplicated module names.")
            modules = []
            for imported in importsPair.value.getElements():
                modules.append(imported.string)
            modulesDict[modulenamePair.value.string] = modules
        
        sortedModules = []
        modules = modulesDict.keys()
        print(modulesDict)
        while True:
            before = len(sortedModules)
            for module in modules: 
                if set(modulesDict[module]) <= set(sortedModules):
                    sortedModules.append(module)
                    modules.remove(module)
            if before == len(sortedModules) and len(modules) != 0:
                raise LogicError(filename, "Cannot resolve module dependencies in {}".format(modules))
            if before == len(sortedModules) and len(modules) == 0:
                break
        
        filenameSorted = []
        for module in sortedModules:
            for filename in self.parsedDict.keys():
                if module == self.parsedDict[filename].getPair("moduleName").value.string:
                    filenameSorted.append(filename)
        
        return filenameSorted
                
                