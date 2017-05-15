/* File generated automatically from ASN.1 JSON description
 */

typedef struct {
	struct {
		struct {
			int elements[5];
		} elements[2];
	} elements[2];
} Myseq;


/* Main function */
int main(int argc, char *argv[]) {

	Myseq seqseq = {
		.elements = { {
			.elements = { {
				.elements = { 1, 2, 3, 4, 5 }
			}, {
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