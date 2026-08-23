#include <iostream>
#include <string>

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-photo-0.1 event=" << name << " detail=" << detail << "\n";
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("ephoto-ready", "library=eos://media/library capture=permission-required");
        event("carrousel", "index=eos://media/index ai=local-opt-in labels=empty-by-default");
        event("editor", "mode=non-destructive export=explicit");
        event("privacy", "upload=disabled face-recognition=not-implemented");
        return 0;
    }
    std::cout << "eos-photod: protocol eos-photo-0.1; use --self-test\n";
    return 0;
}
