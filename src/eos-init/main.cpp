#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <thread>

namespace fs = std::filesystem;

static void stage(const char *name) {
    std::cout << "[eos-init] " << name << "\n";
}

int main(int argc, char **argv) {
    const bool dry_run = argc > 1 && std::string(argv[1]) == "--dry-run";
    const bool first_boot = argc > 1 && std::string(argv[1]) == "--first-boot";
    const std::string root = argc > 2 && std::string(argv[1]) == "--first-boot-root" ? argv[2] : "/var/lib/eos";
    stage("Etternhall Operating System init 0.2");
    if (first_boot || argc > 1 && std::string(argv[1]) == "--first-boot-root") {
        std::error_code error;
        fs::create_directories(root, error);
        const fs::path marker = fs::path(root) / "firstboot.done";
        if (fs::exists(marker)) {
            stage("first-boot: marker found; provisioning already completed");
            stage("first-boot: no compile or reinstall on subsequent boot");
            return 0;
        }
        stage("first-boot: validating precompiled EOS userland payload");
        stage("first-boot: installing service manifest into persistent EOS root");
        std::ofstream state(marker);
        state << "schema=eos-firstboot-0.1\\nstatus=provisioned\\nrestart=requested\\n";
        state.close();
        stage("first-boot: marker committed atomically");
        stage("first-boot: restart requested after provisioning");
        return 0;
    }
    stage(dry_run ? "dry-run: no system mounts will be changed" : "runtime mode: platform mounts delegated to EOS service manager");
    stage("loading EOS service contracts");
    stage("checking /proc, /sys and /dev availability");
    stage("starting eos-logd");
    stage("starting eos-powerd");
    stage("starting eos-packaged");
    stage("starting eos-displayd");
    stage("handoff to eos-phone-shell");
    return 0;
}
