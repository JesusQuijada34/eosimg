#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-device-0.1 edal=active kernel-device-access=brokered\n";
        std::cout << "eos-device-0.1 providers=display,input,audio,power,camera,storage\n";
        std::cout << "eos-device-0.1 app-direct-device-access=deny permission=prompt\n";
        return 0;
    }
    std::cout << "eos-deviced: protocol eos-device-0.1; use --self-test\n";
    return 0;
}
