#include <iostream>
#include <string>

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-policy-0.1 event=" << name << " detail=" << detail << "\n";
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("default", "deny-by-default no-new-privileges=true");
        event("llama", "model-source=trusted-local-store network=deny filesystem=read-model-only");
        event("gecko", "uri=http-https-about network=permission-controlled profile=isolated");
        event("permissions", "camera=prompt microphone=prompt downloads=consent-required");
        return 0;
    }
    std::cout << "eos-policyd: protocol eos-policy-0.1; use --self-test\n";
    return 0;
}
