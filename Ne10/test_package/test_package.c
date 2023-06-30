#include <stdio.h>
#include <string.h>

#include <ne10/NE10.h>

int main(int argc, char *argv[]) {
    ne10_result_t initres = ne10_init();
    ne10_result_t hasNeon = ne10_HasNEON();
    ne10_fft_cfg_int32_t cfg_c = ne10_fft_alloc_c2c_int32 (100);
	return 0;
}
