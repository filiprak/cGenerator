'''
Created on 16.04.2017

@author: raqu
'''

class TestError(Exception):
    
    def __init__(self, message):
        self.message = "TestFail: " + str(message)
        
    def __str__(self):
        return repr(self.message)