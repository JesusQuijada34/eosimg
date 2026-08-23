#include <iostream>
#include <string>

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-browser-0.1 event=" << name << " detail=" << detail << "\n";
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("profile-ready", "root=eos://profiles/default cache=eos://cache/browser");
        event("navigation-planned", "uri=https://example.invalid/ network=disabled");
        event("download-planned", "queue=eos://downloads pending=0 network=disabled");
        event("permissions", "camera=prompt microphone=prompt location=prompt");
        return 0;
    }
    std::cout << "eos-browserd: protocol eos-browser-0.1; no web engine attached; use --self-test\n";
    return 0;
}
