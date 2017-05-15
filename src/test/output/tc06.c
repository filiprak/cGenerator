/* File generated automatically from ASN.1 JSON description
 */

typedef enum { BLACK, BLUE, ORANGE, YELLOW } Color;

typedef enum { BLACK1, BLUE1, ORANGE1, YELLOW1 } Color1;

typedef struct {
	double x;
	Color y;
	struct {
		Color elements[3];
	} z;
} Vector;

typedef struct {
	Color1 c1;
	Color1 c2;
	Color1 c3;
	Color1 c4;
} ColVect;


/* Main function */
int main(int argc, char *argv[]) {

	Color col = BLACK;
	
	Color col1 = BLACK;
	
	ColVect mycolvect = {
		.c1 = ORANGE1,
		.c2 = BLACK1,
		.c3 = ORANGE1,
		.c4 = ORANGE1
	};
	
	Vector myvect = {
		.x = 3.0,
		.y = BLACK,
		.z = {
			.elements = { BLACK, col, col1 }
		}
	};	
	
	return 0;
}