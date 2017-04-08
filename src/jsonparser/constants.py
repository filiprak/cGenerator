
class Token(object):
    BEGIN_OBJECT = 0 # = '{'
    END_OBJECT = 1 # = '}'
    BEGIN_ARRAY = 2 # = '['
    END_ARRAY = 3 # = ']'
    COLON = 4 # = '='
    COMA = 5 # = ','
    NUMBER = 6 # float or integer value
    LITERAL = 7 # string null, false, true
    STRING = 8 # normal string
    
    @staticmethod
    def toString(token):
        if token == None:
            return None
        if token == Token.BEGIN_OBJECT:
            return "BEGIN_OBJECT"
        elif token == Token.END_OBJECT:
            return "END_OBJECT"
        elif token == Token.BEGIN_ARRAY:
            return "BEGIN_ARRAY"
        elif token == Token.END_ARRAY:
            return "END_ARRAY"
        elif token == Token.COLON:
            return "COLON"
        elif token == Token.COMA:
            return "COMA"
        elif token == Token.NUMBER:
            return "NUMBER"
        elif token == Token.LITERAL:
            return "LITERAL"
        elif token == Token.STRING:
            return "STRING"
        else:
            return None

