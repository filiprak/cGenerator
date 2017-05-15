# cGenerator
Python C code generator for initializing data structures based on JSON description

Quick running&testing guide:

To run program use command:
	cd cGenerator/src/
	python main.py "args"
	or bash script ./run.sh

To test program use command:
	cd cGenerator/src/test
	python test.py
	or bash script ./testall.sh
	
Running lexer test:
	cd cGenerator/src/test
	python lexerTest.py
	
Running parser test:
	cd cGenerator/src/test
	python parserTest.py



usage: main.py [-h] [-o output-file] -json json-file-list [json-file-list ...]

[TKOM] ASN.1 & ACN JSON description to C translator

optional arguments:
  -h, --help            show this help message and exit
  -o output-file        Output translator C file name.
  -json json-file-list [json-file-list ...]
                        Input JSON files with ASN.1 data description.

