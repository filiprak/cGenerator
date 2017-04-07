
class Token():
    BEGIN_OBJECT = 0 # = '{'
    END_OBJECT = 1 # = '}'
    BEGIN_ARRAY = 2 # = '['
    END_ARRAY = 3 # = ']'
    COLON = 4 # = '='
    COMA = 5 # = ','
    NUMBER = 6 # float or integer value
    LITERAL = 7 # string ‘null’, ‘false’ lub ‘true’
    STRING = 8 # normal string
    QUOTE = 9 # = ‘ “ ‘