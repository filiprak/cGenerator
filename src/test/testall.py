'''
Created on 16.04.2017
This script runs all available tests
@author: raqu
'''
import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)
from main import main as test

class Format():
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def filediff(f1, f2):
    with open(f1, 'r') as file1:
        with open(f2, 'r') as file2:
            lines1 = file1.readlines()
            lines2 = file2.readlines()
            for i in range(len(lines1)):
                if i >= len(lines1) or i >= len(lines2):
                    return False, lines1[i-1], lines2[i-1]
                
                if lines1[i] != lines2[i]:
                    return False, lines1[i], lines2[i]
            return True, None, None

NRTESTCASES = 7

messages = []
outputdir = "output"
#clear output directory
filelist = [ f for f in os.listdir(outputdir) if f.endswith(".c") ]
for f in filelist:
    os.remove(outputdir + "/" + f)

for i in range(1, NRTESTCASES+1):
    filename = "alltestcases/tc{}.json".format(str(i).rjust(2, '0'))
    filenameexp = "alltestcases/tc{}.c".format(str(i).rjust(2, '0'))
    outputfile = "output/tc{}.c".format(str(i).rjust(2, '0'))
    test(parseargs=False, files=[filename], outputfile=outputfile, adddate=False)
    
    same, line1, line2 = filediff(outputfile, filenameexp)
    if not same:
        message = "TEST CASE {} FAILED".format(filename)
        message += "\n+\t" + line1 
        message += "\n-\t" + line2
        messages.append(Format.FAIL + Format.BOLD + message + Format.ENDC + Format.ENDC)
    else:
        message = "TEST CASE {} PASSED".format(filename)
        messages.append(Format.OKGREEN + Format.BOLD + message + Format.ENDC + Format.ENDC)

for m in messages:
    print(m)

    
