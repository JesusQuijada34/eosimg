#include <iostream>
#include <string>

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "eos-audio-0.1 input=microphone permission=prompt hardware=disabled\n";
        std::cout << "eos-audio-0.1 output=tts permission=prompt backend=local-only\n";
        std::cout << "eos-audio-0.1 events=listening,thinking,speaking waves=eos-immersived\n";
        return 0;
    }
    std::cout << "eos-audiod: protocol eos-audio-0.1; use --self-test\n";
    return 0;
}
