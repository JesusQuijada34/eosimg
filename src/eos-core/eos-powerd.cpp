#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-power-0.1 battery=edal-managed charging=edal-managed\n";
        std::cout << "eos-power-0.1 suspend=policy-controlled display-timeout=policy-controlled\n";
        std::cout << "eos-power-0.1 thermal=monitor-only hardware=abstracted\n";
        return 0;
    }
    std::cout << "eos-powerd: protocol eos-power-0.1; use --self-test\n";
    return 0;
}
