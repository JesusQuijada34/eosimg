#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-net-0.1 default=deny dns=eos-resolver tls=required\n";
        std::cout << "eos-net-0.1 browser=consent-only downloads=consent-only\n";
        std::cout << "eos-net-0.1 assistant=deny model-store=consent-only\n";
        std::cout << "eos-net-0.1 app-sockets=brokered no-direct-kernel-sockets=true\n";
        return 0;
    }
    std::cout << "eos-netd: protocol eos-net-0.1; use --self-test\n";
    return 0;
}
