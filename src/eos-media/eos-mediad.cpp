#include <iostream>
#include <string>

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-media-0.1 event=" << name << " detail=" << detail << "\n";
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("library-ready", "root=eos://media/library");
        event("metadata", "photo=enabled audio=enabled video=enabled");
        event("playback-policy", "local-files=allowed protected-content=platform-authorized-only");
        event("capture-policy", "camera=mediad-owned microphone=permission-required");
        return 0;
    }
    std::cout << "eos-mediad: protocol eos-media-0.1; use --self-test\n";
    return 0;
}
