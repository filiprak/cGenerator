'''
Created on 9.05.2017
Constants module for semantic analyzer
@author: raqu
'''
import re

reservedCKeywords = [
        "auto",
        "break",
        "case",
        "char",
        "const",
        "continue",
        "default",
        "do",
        "double",
        "else",
        "enum",
        "extern",
        "float",
        "for",
        "goto",
        "if",
        "int",
        "long",
        "register",
        "return",
        "short",
        "signed",
        "sizeof",
        "static",
        "struct",
        "switch",
        "typedef",
        "union",
        "unsigned",
        "void",
        "volatile",
        "while"
    ]

asn1types = [
    "BOOLEAN",
    "INTEGER",
    "REAL",
    "BIT STRING",
    "OCTET STRING",
    "CHARACTER STRING",
    "ENUMERATED",
    "SEQUENCE",
    "SEQUENCE OF",
    "SET",
    "SET OF",
    "CHOICE"
    ]

# helper functions for validation c indentifiers and typenames
def validCTypename(typename):
    if typename in reservedCKeywords:
        return False
    if ' ' in typename or '\n' in typename or '\r' in typename or '\t' in typename:
        return False
    return re.match("^[_a-zA-Z][_a-zA-Z0-9]*$" , typename) != None
    
def validCidentifier(identifier):
    if identifier in reservedCKeywords:
        return False
    if ' ' in identifier or '\n' in identifier or '\r' in identifier or '\t' in identifier:
        return False
    return re.match("^[_a-zA-Z][_a-zA-Z0-9]*$" , identifier) != None
