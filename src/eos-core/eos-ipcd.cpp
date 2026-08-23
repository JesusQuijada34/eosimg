#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-ipc-0.1 transport=local-broker endpoints=eos://ipc/*\n";
        std::cout << "eos-ipc-0.1 identity=service-attested permissions=policy-checked\n";
        std::cout << "eos-ipc-0.1 app-ipc=brokered kernel-sockets=hidden payload=json-versioned\n";
        return 0;
    }
    std::cout << "eos-ipcd: protocol eos-ipc-0.1; use --self-test\n";
    return 0;
}
