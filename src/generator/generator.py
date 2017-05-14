'''
Created on 09.05.2017
Code generator module. Generator takes all declarations, definitions and defines
objects and converts them to string, then forms that string correctly and
dumps it to specified file.
@author: raqu
'''
from datetime import datetime
from ctypes import indent


class Generator():
    '''
    Generator takes all declarations, definitions and defines
    objects and converts them to string, then forms that string correctly and
    dumps it to specified file.
    '''
    def __init__(self):
        self.filestring = ""
        
    def generate(self, macr, decl, defi, adddate=True):
        '''
        Converts given C clauses to string C code
        :param macr: list containing CPreprocConstDefine type elements
        :param decl: list containing CTypedef, CVarType type elements
        :param defi: list containing CVarAssign elements
        '''
        
        header = "File generated automatically from ASN.1 JSON description\n"
        if adddate:
            date = datetime.today()
            header += "Generation date:  " + date.strftime("%Y-%m-%d %H:%M")
        
        contents = ""
        if len(macr) > 0:
            contents = "\n\n"
            for macrodef in macr:
                contents += str(macrodef) + "\n"
        
        if len(decl) > 0:
            contents += "\n\n"
            for declaration in decl:
                contents += str(declaration) + "\n\n"
        
        contents += "\n"
        contents += self.comment("Main function")
        contents += "\n"
        
        maincontents = ""
        if len(defi) > 0:
            for definition in defi:
                maincontents += str(definition) + "\n\n"
        
        self.filestring += self.comment(header)
        self.filestring += contents + self.mainfunc(maincontents)
        return self.filestring
    
    def comment(self, text):
        '''
        Generate C comment
        :param text: commented text
        '''
        string = "/* " + str(text) + " */"
        return string
    
    def mainfunc(self, contents):
        '''
        Generate main function in C style
        :param contents: main function body
        '''
        mainfunc = "int main(int argc, char *argv[]) {\n\n"
        mainfunc += indent(contents)
        mainfunc += indent("\n\nreturn 0;")
        mainfunc += "\n}"
        return mainfunc
    
    def saveFile(self, filename):
        '''
        Dumps generated string to file named by filename string parameter
        :param filename: name of file to dump C code to
        '''
        print(self.filestring)
        try:
            with open(filename, "w") as f:
                f.write(self.filestring)
            
        except IOError as ioErr:
            ioErr.args += (filename,)
            raise
        
            
    
