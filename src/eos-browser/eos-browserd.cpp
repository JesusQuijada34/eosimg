#include <iostream>
#include <string>

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-browser-0.2 event=" << name << " detail=" << detail << "\n";
}

bool allowed_uri(const std::string &uri) {
    return uri.rfind("https://", 0) == 0 || uri.rfind("http://", 0) == 0 || uri.rfind("about:", 0) == 0;
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("profile-ready", "root=eos://profiles/default cache=eos://cache/browser");
        event("navigation-planned", "uri=https://example.invalid/ network=disabled");
        event("download-planned", "queue=eos://downloads pending=0 network=disabled");
        event("permissions", "camera=prompt microphone=prompt location=prompt");
        event("gecko-session", "runtime=eos-gecko-0.1 session=eos://browser/session/default");
        return 0;
    }
    if (argc == 5 && std::string(argv[1]) == "--plan-uri" && std::string(argv[3]) == "--profile") {
        const std::string uri = argv[2];
        const std::string profile = argv[4];
        if (!allowed_uri(uri)) {
            std::cerr << "eos-browserd error: URI scheme is not allowed\n";
            return 2;
        }
        if (profile.empty() || profile.find("..") != std::string::npos) {
            std::cerr << "eos-browserd error: invalid isolated profile\n";
            return 2;
        }
        event("navigation-planned", "uri=" + uri + " network=policy-controlled");
        event("gecko-session", "runtime=eos-gecko-0.1 profile=" + profile);
        return 0;
    }
    std::cout << "eos-browserd: protocol eos-browser-0.2; use --self-test or --plan-uri <uri> --profile <name>\n";
    return 0;
}
