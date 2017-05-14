/* File generated automatically from ASN.1 JSON description
 */

#define FALV_	0
#define TRUE_	1
#define FALV	0
#define TRUEV	1


typedef struct {
	int elements[5];
} Vector;

typedef struct {
	double elements[5];
} Vector1;

typedef struct {
	float elements[5];
} Vector8;

typedef struct {
	int elements[5];
} Vector9;

typedef int Myint;

typedef struct {
	int elements[5];
} Vector7;

typedef int Mybool;


/* Main function */
int main(int argc, char *argv[]) {

	Vector1 myvect1 = {
		.elements = { 1.0, 2.1, -3.4, 4.0, 5.4 }
	};
	
	Vector myvect = {
		.elements = { 1, 2, 3, 4, 5 }
	};
	
	Vector8 realseq = {
		.elements = { 1.0, 0.002, 3.1, 0.4, -3.2e-08 }
	};
	
	Myint r = 3;
	
	int i = 3;
	
	Vector9 intseq = {
		.elements = { 1, i, i, 1, 1 }
	};
	
	Mybool b = 1;
	
	Mybool a = FALV;
	
	Vector7 boolseq = {
		.elements = { TRUE_, 1, b, 0, 0 }
	};	
	
	return 0;
}