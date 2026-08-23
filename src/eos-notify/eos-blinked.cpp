#include <iostream>
#include <string>

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-blinke-0.1 event=" << name << " detail=" << detail << "\n";
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("safe-area", "top=64 bottom=0 left=0 right=0 units=eosdp");
        event("notification", "source=com.etternhall.eos.notes priority=normal surface=blinke");
        event("notch", "reserved=true occlusion=blocked edge-light=available");
        event("window-api", "behind-notch=layout-aware controls=accessible");
        return 0;
    }
    std::cout << "eos-blinked: protocol eos-blinke-0.1; use --self-test\n";
    return 0;
}
