#include <chrono>
#include <filesystem>
#include <iostream>
#include <string>
#include <thread>

namespace fs = std::filesystem;

static void stage(const char *name) {
    std::cout << "[eos-init] " << name << "\n";
}

int main(int argc, char **argv) {
    const bool dry_run = argc > 1 && std::string(argv[1]) == "--dry-run";
    stage("Etternhall Operating System init 0.1");
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
