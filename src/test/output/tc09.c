/* File generated automatically from ASN.1 JSON description
 */

#define TrueVal	1


typedef struct {
	int bool;
	int integ;
	double real;
	struct {
		int string[2];
	} bitstr;
	struct {
		char string[3];
	} octstr;
	struct {
		char string[32];
	} charstr;
	enum { ENUMVAL0, ENUMVAL1, ENUMVAL2, ENUMVAL3 } enumval;
} Sequence;


/* Main function */
int main(int argc, char *argv[]) {

	int bool = 0;
	
	int integ = 3;
	
	double real = 0.045974;
	
	struct {
		int string[2];
	} bitstr = {
		.string = { 0xaabbccdd, 0x11223344 }
	};
	
	struct {
		char string[3];
	} octstr = {
		.string = { 0b00000000, 0b11111111, 0b00001111 }
	};
	
	struct {
		char string[32];
	} charstr = {
		.string = "lorem ipsum dolor sit amet\n\t\r"
	};
	
	enum { VALUE_, VALUE__, VALUE___ } enumval = VALUE_;
	
	Sequence seq = {
		.bool = bool,
		.integ = integ,
		.real = real,
		.bitstr = {
			.string = { 0x00223344, 0x7766ffaa }
		},
		.octstr = {
			.string = { 0xff, 0xff, 0xff }
		},
		.charstr = {
			.string = "042h1#%U^HT#%#$EGHhRWg%Y^THGBHWH"
		},
		.enumval = ENUMVAL1
	};	
	
	return 0;
}