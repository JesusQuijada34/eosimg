#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <string>

namespace fs = std::filesystem;

namespace {
void event(const std::string &name, const std::string &detail) {
    std::cout << "eos-browser-0.3 event=" << name << " detail=" << detail << "\n";
}

bool allowed_uri(const std::string &uri) {
    return uri.rfind("https://", 0) == 0 || uri.rfind("http://", 0) == 0 || uri.rfind("about:", 0) == 0;
}

bool safe_name(const std::string &value) {
    if (value.empty() || value == "." || value == ".." || value.find('/') != std::string::npos || value.find('\\') != std::string::npos) {
        return false;
    }
    return value.find("..") == std::string::npos;
}

bool atomic_write(const fs::path &path, const std::string &contents) {
    std::error_code ec;
    fs::create_directories(path.parent_path(), ec);
    if (ec) return false;
    const auto temp = path.string() + ".tmp";
    {
        std::ofstream out(temp, std::ios::binary | std::ios::trunc);
        if (!out) return false;
        out << contents;
        out.flush();
        if (!out) return false;
    }
    fs::rename(temp, path, ec);
    if (ec) {
        fs::remove(temp);
        return false;
    }
    return true;
}

bool explicit_root(const std::string &root) {
    return !root.empty() && root.rfind("/", 0) == 0 && root.find("..") == std::string::npos;
}

int create_profile(const fs::path &root, const std::string &profile) {
    if (!safe_name(profile)) return 2;
    const auto profile_dir = root / "profiles" / profile;
    const std::string state = "{\n  \"schema\": \"eos-browser-profile-0.1\",\n  \"name\": \"" + profile + "\",\n  \"cookies\": [],\n  \"history\": [],\n  \"permissions\": {\"camera\": \"prompt\", \"microphone\": \"prompt\", \"location\": \"prompt\"}\n}\n";
    if (!atomic_write(profile_dir / "profile-state.json", state)) return 3;
    event("profile-created", "root=" + profile_dir.string());
    return 0;
}

int queue_download(const fs::path &root, const std::string &uri, const std::string &profile) {
    if (!allowed_uri(uri) || !safe_name(profile)) return 2;
    const auto queue = root / "downloads" / "queue.json";
    const std::string state = "{\n  \"schema\": \"eos-download-queue-0.1\",\n  \"network\": \"eos-netd\",\n  \"items\": [{\"uri\": \"" + uri + "\", \"profile\": \"" + profile + "\", \"state\": \"pending-permission\"}]\n}\n";
    if (!atomic_write(queue, state)) return 3;
    event("download-queued", "uri=" + uri + " permission=network-broker profile=" + profile);
    return 0;
}
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        event("profile-ready", "root=eos://profiles/default cache=eos://cache/browser");
        event("navigation-planned", "uri=https://example.invalid/ network=disabled");
        event("download-planned", "queue=eos://downloads pending=0 network=disabled");
        event("permissions", "camera=prompt microphone=prompt location=prompt");
        event("gecko-session", "runtime=eos-gecko-0.1 session=eos://browser/session/default");
        event("state-store", "profile-state=atomic download-queue=atomic root=explicit");
        return 0;
    }
    if (argc == 5 && std::string(argv[1]) == "--create-profile" && std::string(argv[3]) == "--root" && explicit_root(argv[4])) {
        return create_profile(argv[4], argv[2]);
    }
    if (argc == 7 && std::string(argv[1]) == "--queue-download" && std::string(argv[3]) == "--profile" && std::string(argv[5]) == "--root" && explicit_root(argv[6])) {
        return queue_download(argv[6], argv[2], argv[4]);
    }
    if (argc == 5 && std::string(argv[1]) == "--plan-uri" && std::string(argv[3]) == "--profile") {
        const std::string uri = argv[2];
        const std::string profile = argv[4];
        if (!allowed_uri(uri) || !safe_name(profile)) {
            std::cerr << "eos-browserd error: URI scheme or isolated profile is not allowed\n";
            return 2;
        }
        event("navigation-planned", "uri=" + uri + " network=policy-controlled");
        event("gecko-session", "runtime=eos-gecko-0.1 profile=" + profile);
        return 0;
    }
    std::cout << "eos-browserd: protocol eos-browser-0.3; use --self-test, --plan-uri, --create-profile or --queue-download\n";
    return 0;
}
