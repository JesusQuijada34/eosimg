#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-display-0.1 modes=portrait,landscape rotation=policy-controlled\n";
        std::cout << "eos-display-0.1 touch=enabled compositor=eos-windowd vsync=managed\n";
        std::cout << "eos-display-0.1 hdr=optional color-profile=eos-default hardware=abstracted\n";
        return 0;
    }
    std::cout << "eos-displayd: protocol eos-display-0.1; use --self-test\n";
    return 0;
}
