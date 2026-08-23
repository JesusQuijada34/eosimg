#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-market-0.1 catalog=local signed-eapp-only network=disabled\n";
        std::cout << "eos-market-0.1 metadata=identity,version,api,license,permissions,sha256\n";
        std::cout << "eos-market-0.1 install=eos-packaged consent=required launcher=eos-launcherd\n";
        std::cout << "eos-market-0.1 reject=deb,appimage,linux-elf\n";
        return 0;
    }
    std::cout << "eos-marketd: protocol eos-market-0.1; use --self-test\n";
    return 0;
}
