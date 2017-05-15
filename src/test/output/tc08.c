/* File generated automatically from ASN.1 JSON description
 */

#define FALSZ	0
#define PRAWDA	1


typedef int Mybool;

typedef unsigned Myint;

typedef float Myreal;

typedef enum { E1, E2, E3 } Myenum;

typedef struct {
	int string[1];
} Mybitstr;

typedef struct {
	char string[8];
} Myoctstr;

typedef struct {
	char string[8];
} Mycharstr;

typedef struct {
	Myenum enumer;
	Myoctstr octets;
} Myseq;

typedef struct {
	Mybool elements[6];
} Myseqof;

typedef struct {
	struct {
		int string[1];
	} bits;
	struct {
		char string[3];
	} octets;
	struct {
		char string[3];
	} chars;
} Myset;

typedef struct {
	Myint elements[6];
} Mysetof;

typedef union {
	struct {
		int string[1];
	} bits;
	Myenum enums;
	Mycharstr chars;
} Mychoice;

typedef struct {
	Myint myint;
	Mybool mybool;
	Myreal myreal;
	Myenum myenum;
	Mybitstr bstring;
	Myoctstr ostring;
	Mycharstr cstring;
	Myseq myseq;
	Myseqof myseqof;
	Myset myset;
	Mysetof mysetof;
	Mychoice mychoice;
} Seqofall;


/* Main function */
int main(int argc, char *argv[]) {

	Myint myint = 9;
	
	Myint myint1 = 10;
	
	Myint myint2 = 1;
	
	Mybool mybool = PRAWDA;
	
	Mybool mybool1 = 0;
	
	Mybool mybool2 = 1;
	
	Myreal myreal = -2.5;
	
	Myenum myenum = E2;
	
	Mybitstr mybitstr = {
		.string = { 0b10011010000000000000000000000000 }
	};
	
	Myoctstr myoctstr = {
		.string = { 0xff, 0xaa, 0x34, 0xfb, 0xdd, 0x56, 0x32, 0x01 }
	};
	
	Mycharstr mycharstr = {
		.string = "ciagznak"
	};
	
	Myseq myseq = {
		.enumer = myenum,
		.octets = myoctstr
	};
	
	Myseqof myseqof = {
		.elements = { PRAWDA, mybool, 0, 1, mybool1, mybool2 }
	};
	
	Myset myset = {
		.bits = {
			.string = { 0b11100000000000000000000000000000 }
		},
		.octets = {
			.string = { 0xab, 0xcd, 0xef }
		},
		.chars = {
			.string = "123"
		}
	};
	
	Mysetof mysetof = {
		.elements = { 2, myint, myint2, 1, myint1, 5 }
	};
	
	Mychoice mychoice = {
		.bits = {
			.string = { 0b10100000000000000000000000000000 }
		}
	};
	
	Mychoice mychoice1 = {
		.chars = {
			.string = "a1b2b3%$"
		}
	};
	
	Mychoice mychoice2 = {
		.enums = E3
	};
	
	Seqofall allobjects = {
		.myint = myint1,
		.mybool = mybool2,
		.myreal = myreal,
		.myenum = myenum,
		.bstring = mybitstr,
		.ostring = myoctstr,
		.cstring = mycharstr,
		.myseq = myseq,
		.myseqof = myseqof,
		.myset = myset,
		.mysetof = mysetof,
		.mychoice = mychoice
	};	
	
	return 0;
}