/* File generated automatically from ASN.1 JSON description
 */

#define FALSZ	0
#define PRAWDA	1


typedef enum { BLACK, BLUE, ORANGE, YELLOW } Color;

typedef int Mybool;

typedef struct {
	Mybool flag;
	Color color;
	struct {
		Mybool elements[3];
	} boolsequence;
} MySequence;


/* Main function */
int main(int argc, char *argv[]) {

	int flag1 = 1;
	
	Mybool flag2 = 0;
	
	Mybool flag3 = PRAWDA;
	
	int flag4 = 0;
	
	Color col1 = BLACK;
	
	MySequence myseq = {
		.flag = flag1,
		.color = BLACK,
		.boolsequence = {
			.elements = { 0, FALSZ, PRAWDA }
		}
	};	
	
	return 0;
}