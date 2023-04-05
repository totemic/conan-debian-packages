#include <flatcc/flatcc_builder.h>

int main(int argc, char *argv[]) {
    flatcc_builder_t builder;
    flatcc_builder_init(&builder);

    void* p = flatcc_builder_aligned_alloc(1, 4);    
    flatcc_builder_aligned_free(p);
    
    flatcc_builder_clear(&builder);
    return 0;
}