#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-window-0.1 display=1080x2400 notch-top=80 safe-area=0,80,1080,2320\n";
        std::cout << "eos-window-0.1 register=browser content-rect=0,80,1080,2320 occlusion-aware=true\n";
        std::cout << "eos-window-0.1 register=panel reserved=notch-controls focus-safe=true\n";
        return 0;
    }
    std::cout << "eos-windowd: protocol eos-window-0.1; use --self-test\n";
    return 0;
}
