'''
Created on 28.04.2017
Semantic analyzer main module,
contains functions of semantic actions over parsed file
@author: raqu
'''
from errors import LogicError
from contentsresolver import ContentsResolver


class SemanticAnalyzer():    
    def analyze(self, parsedDict, jsonFilelines):
        '''
        Main method, analyzes parsed files, returns declarations, definitions and defines if 
        :param parsedDict: dict: key: filename, value: parsed jsonfile
        :param jsonFilelines: dict: key: file name, value: dict: (key: jsonobj, value: its line number in file)
        '''
        if len(parsedDict.keys()) == 0:
            return None
        processOrder = self.dependencySort(parsedDict, jsonFilelines)
        
        contentResolver = ContentsResolver()
        return contentResolver.resolve(processOrder, parsedDict, jsonFilelines)
    
    
    def dependencySort(self, parsedDict, jsonFilelines):        
        '''
        Method for validating module dependencies and determine files processing order
        :param parsedDict: dict: key: filename, value: parsed jsonfile
        :param jsonFilelines: dict: key: file name, value: dict: (key: jsonobj, value: its line number in file)
        '''
        for filename in parsedDict.keys():
            parsed = parsedDict[filename]
            line = jsonFilelines[filename][parsed]
            modulenamePair = parsed.getPair("moduleName")
            if not modulenamePair:
                raise LogicError(filename, "Module name tag required: \"moduleName\":<name>", line)
            if not modulenamePair.holdsString():
                raise LogicError(filename, "Incorrect value, should be string value\"moduleName\":<string>", line)
            importsPair = parsed.getPair("imports")
            if importsPair:
                if not importsPair.holdsArray():
                    raise LogicError(filename, "Incorrect imports value\"imports\":[ names ]", line)
                if not importsPair.value.holdsOnlyStrings():
                    raise LogicError(filename, "Incorrect imports value\"imports\":[ \"module1\", \"module2\", ...  ]", line)

        modulesDict = dict()
        for filename in parsedDict.keys():
            parsed = parsedDict[filename]
            modulenamePair = parsed.getPair("moduleName")
            importsPair = parsed.getPair("imports")
            if modulenamePair in modulesDict.keys():
                raise LogicError(filename, "Duplicated module names.", line)
            modules = []
            if importsPair:
                for imported in importsPair.value.getElements():
                    modules.append(imported.string)
            modulesDict[modulenamePair.value.string] = modules
        
        sortedModules = []
        modules = modulesDict.keys()
        
        while True:
            before = len(sortedModules)
            for module in modules: 
                if set(modulesDict[module]) <= set(sortedModules):
                    sortedModules.append(module)
                    modules.remove(module)
            if before == len(sortedModules) and len(modules) != 0:
                raise LogicError("dependency check", "Cannot resolve module dependencies in {}".format(modules), line)
            if before == len(sortedModules) and len(modules) == 0:
                break
        
        filenameSorted = []
        for module in sortedModules:
            for filename in parsedDict.keys():
                if module == parsedDict[filename].getPair("moduleName").value.string:
                    filenameSorted.append(filename)
        
        return filenameSorted
                
                