#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-model-0.1 store=trusted-local-only format=GGUF revision=pinned\n";
        std::cout << "eos-model-0.1 consent=required license=required sha256=required\n";
        std::cout << "eos-model-0.1 download=disabled runtime=offline ram-budget=selector-managed\n";
        return 0;
    }
    std::cout << "eos-modeld: protocol eos-model-0.1; use --self-test\n";
    return 0;
}
