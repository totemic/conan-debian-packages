#include <gpiod.hpp>

#include <iostream>

int main() {
    for (auto& it: gpiod::make_chip_iter()) {
        std::cout
            << it.name() << " ["
            << it.label() << "] ("
            << it.num_lines() << " lines)"
            << ::std::endl;
    }

    return EXIT_SUCCESS;
}
