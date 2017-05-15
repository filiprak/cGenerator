'''
Created on 15.03.2017
Main module contains main() function
@author: raqu
'''

from jsonparser.lexer import JSONLexer
from errors import LexerError, ParserError, LogicError, CSerializeError, Format
from jsonparser.jsonparser import JSONParser
from semantic_analyzer.semantic import SemanticAnalyzer
import argparse
from generator.generator import Generator
import sys


'''DEBUG'''
def tracefunc(frame, event, arg, indent=[0]):
    substring_list = ["assign"]
    if not any(substring in frame.f_code.co_name for substring in substring_list):
        return tracefunc
    
    if event == "call":
        indent[0] += 1
        print "| " * indent[0], "call function", frame.f_code.co_name
    elif event == "return":
        #print "| " * indent[0], "exit function", frame.f_code.co_name
        indent[0] -= 1
    return tracefunc

sys.settrace(tracefunc)
'''DEBUG'''


def parseArgs():
    '''
    Responsible for arguments parsing from input:
        -json: json files list
        -o: output C file name
    '''
    argparser = argparse.ArgumentParser(description='[TKOM] ASN.1 & ACN JSON description to C translator')
    argparser.add_argument('-o', action='store', metavar="output-file", help='Output translator C file name.')
    argparser.add_argument('-json', metavar="json-file-list", nargs='+', required=True,
                           help='Input JSON files with ASN.1 data description.')
    return argparser.parse_args()
    

def main(parseargs=True, files=[], outputfile="out.c", adddate=False):
    '''
    Main program function
    '''
    # parse program arguments
    if parseargs:
        args = parseArgs()
        
        # output file name
        if args.o != None:
            outputfile = str(args.o)
        
        # json file paths to parse
        files = args.json
    
    # create instances of tools for translating
    lexer = JSONLexer()
    parser = JSONParser()
    semAnalyzer = SemanticAnalyzer()
    generator = Generator()
    
    # initilize dict for holding parsed files
    parsedDict = dict()
    
    # initialize dict for holding all parsed json object line numbers in files
    jsonobjlines = dict()
    try:
        # loop of parsing files
        for name in files:
            lexer.loadFile(name)
            res = lexer.analyze()
            parsedDict[name] = parser.parse(res, name)
            jsonobjlines[name] = parser.enumerated
        
        # semantic analyze and code generation
        macr, decl, defi = semAnalyzer.analyze(parsedDict, jsonobjlines)
        generator.generate(macr, decl, defi, adddate=adddate)
        generator.saveFile(outputfile)
        
        # print results
        print(Format.OKBLUE + generator.filestring + Format.ENDC)
        
        print(Format.BOLD + "Generation successful..." + Format.ENDC)
        print(Format.BOLD + "Output C file saved in: '{}'...".format(outputfile) + Format.ENDC)
    
    # catch exceptions if occured
    except IOError as ioErr:
        print("I/O error({0}): {1}: {2}".format(ioErr.errno, ioErr.strerror, ioErr.args[2]))
    except LexerError as leErr:
        print(leErr.message)
    except ParserError as paErr:
        print(paErr.message)
    except LogicError as loErr:
        print(loErr.message)
    except CSerializeError as cErr:
        print(cErr.message)



"""start program execution"""
if __name__ == "__main__":
    main(parseargs=True, adddate=False)
    
    
    
    
    
    
    

