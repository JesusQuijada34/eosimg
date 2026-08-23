#include <iostream>
#include <string>

namespace {
void print_state(const std::string &state, const std::string &detail) {
    std::cout << "eos-immersive-0.1 state=" << state << " detail=" << detail << "\n";
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        print_state("idle", "notch=dim wave=off");
        print_state("listening", "notch=edge-glow wave=voice-input");
        print_state("thinking", "notch=edge-glow wave=processing");
        print_state("speaking", "notch=edge-glow wave=assistant-output");
        print_state("idle", "notch=dim wave=off");
        return 0;
    }
    std::cout << "eos-immersived: protocol eos-immersive-0.1; use --self-test\n";
    return 0;
}
