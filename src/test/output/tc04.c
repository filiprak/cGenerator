/* File generated automatically from ASN.1 JSON description
 */

typedef struct {
	int elements[5];
} Innerseqof;

typedef struct {
	struct {
		Innerseqof elements[2];
	} elements[2];
} Myseq;


/* Main function */
int main(int argc, char *argv[]) {

	Innerseqof inside = {
		.elements = { 1, -2, 3, -4, 5 }
	};
	
	Myseq seqseq = {
		.elements = { {
			.elements = { inside, {
				.elements = { 1, 2, 3, 4, 5 }
			} }
		}, {
			.elements = { {
				.elements = { 1, 2, 3, 4, 5 }
			}, {
				.elements = { 1, 2, 3, 4, 5 }
			} }
		} }
	};	
	
	return 0;
}