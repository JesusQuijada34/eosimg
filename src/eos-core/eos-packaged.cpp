#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-package-0.1 format=eapp-v2 signature=ed25519 trusted-key-required\n";
        std::cout << "eos-package-0.1 install-prefix=eos://apps/<bundle-id> payload=isolated\n";
        std::cout << "eos-package-0.1 reject=deb,appimage,linux-elf unsigned=true\n";
        std::cout << "eos-package-0.1 runtime=eosbc permissions=sandbox-policy\n";
        return 0;
    }
    std::cout << "eos-packaged: protocol eos-package-0.1; use --self-test\n";
    return 0;
}
