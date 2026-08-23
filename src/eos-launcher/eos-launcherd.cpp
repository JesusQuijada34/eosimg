#include <iostream>
#include <string>

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-launcher-0.1 event=" << name << " detail=" << detail << "\n";
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("registry-ready", "root=eos://launchers/registry");
        event("provider-policy", "format=eapp signature=required user-elf=blocked");
        event("provider-example", "bundle=com.etternhall.eos.notes capabilities=apps.widgets");
        event("selection", "default=eos-shell confirmation=required");
        return 0;
    }
    std::cout << "eos-launcherd: protocol eos-launcher-0.1; use --self-test\n";
    return 0;
}
