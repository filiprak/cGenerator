/* File generated automatically from ASN.1 JSON description
 */

typedef struct {
	struct {
		int string[1];
	} elements[5];
} Bitseq;

typedef struct {
	struct {
		char string[4];
	} elements[5];
} Octseq;

typedef struct {
	struct {
		char string[4];
	} elements[5];
} Charseq;


/* Main function */
int main(int argc, char *argv[]) {

	Bitseq bitseq = {
		.elements = { {
			.string = { 0b11010000000000000000000000000000 }
		}, {
			.string = { 0xf0000000 }
		}, {
			.string = { 0b01100000000000000000000000000000 }
		}, {
			.string = { 0xa0000000 }
		}, {
			.string = { 0xb0000000 }
		} }
	};
	
	Octseq octseq = {
		.elements = { {
			.string = { 0b11011101, 0b11011101, 0b11011101, 0b11011101 }
		}, {
			.string = { 0xff, 0xff, 0xff, 0xff }
		}, {
			.string = { 0xaf, 0xaf, 0xaf, 0xaf }
		}, {
			.string = { 0xab, 0xab, 0xab, 0xab }
		}, {
			.string = { 0x12, 0x34, 0xab, 0xcd }
		} }
	};
	
	Charseq charseq = {
		.elements = { {
			.string = "1234"
		}, {
			.string = "koty"
		}, {
			.string = "psy0"
		}, {
			.string = ";'.;"
		}, {
			.string = "ssss"
		} }
	};	
	
	return 0;
}