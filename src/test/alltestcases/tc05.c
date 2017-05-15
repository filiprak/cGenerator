/* File generated automatically from ASN.1 JSON description
 */

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
} Set;

typedef union {
	double x;
	union {
		int i;
		int flag;
	} y;
	Set set;
	struct {
		double o;
		float w;
	} z;
} Vector;


/* Main function */
int main(int argc, char *argv[]) {

	Set set01 = {
		.bits = {
			.string = { 0b10000000000000000000000000000000 }
		},
		.octets = {
			.string = { 0x6f, 0xa3, 0xdd }
		},
		.chars = {
			.string = "mam"
		}
	};
	
	Vector myuni = {
		.z = {
			.o = 4.9,
			.w = -30000.0
		}
	};
	
	Vector myuni1 = {
		.set = {
			.bits = {
				.string = { 0b11000000000000000000000000000000 }
			},
			.octets = {
				.string = { 0xff, 0xaa, 0xdd }
			},
			.chars = {
				.string = "abc"
			}
		}
	};	
	
	return 0;
}