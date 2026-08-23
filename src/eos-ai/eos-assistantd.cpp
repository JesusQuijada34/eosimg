#include <iostream>
#include <string>

int main(int argc, char **argv) {
    const bool capabilities = argc > 1 && std::string(argv[1]) == "--capabilities";
    if (capabilities) {
        std::cout << "service=eos-assistantd\n";
        std::cout << "api=eos-ai-0.1\n";
        std::cout << "mode=local-stub\n";
        std::cout << "network=disabled\n";
        std::cout << "model=not-loaded\n";
        std::cout << "consent=required\n";
        return 0;
    }
    std::cout << "eos-assistantd: local assistant service stub; no model loaded\n";
    std::cout << "eos-assistantd: use --capabilities to inspect the service contract\n";
    return 0;
}
