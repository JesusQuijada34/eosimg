#include <cerrno>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>
#include <sys/prctl.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/stat.h>

namespace fs = std::filesystem;

static void set_limit(int resource, rlim_t soft, rlim_t hard) {
    const rlimit limit{soft, hard};
    if (setrlimit(resource, &limit) != 0) {
        throw std::runtime_error("setrlimit failed");
    }
}

int main(int argc, char **argv) {
    if (argc < 5 || std::string(argv[1]) != "--service" || std::string(argv[3]) != "--executable") {
        std::cerr << "usage: eos-supervise --service NAME --executable /path/to/eos-internal-service [--dry-run]\n";
        return 2;
    }
    const std::string service = argv[2];
    const fs::path executable = fs::absolute(argv[4]);
    const bool dry_run = argc > 5 && std::string(argv[5]) == "--dry-run";
    if (!fs::is_regular_file(executable) || access(executable.c_str(), X_OK) != 0) {
        std::cerr << "eos-supervise: executable is missing or not executable\n";
        return 2;
    }
    // Only EOS-internal services may be launched by this supervisor. User apps
    // enter through eos-packaged and the .eapp runtime instead.
    if (executable.filename().string().rfind("eos-", 0) != 0) {
        std::cerr << "eos-supervise: refusing non-EOS internal executable\n";
        return 3;
    }
    std::cout << "service=" << service << " executable=" << executable << " sandbox=no-new-privileges,rlimit-as=512MiB,rlimit-cpu=30s,rlimit-nofile=256,rlimit-nproc=64\n";
    if (dry_run) return 0;

    const pid_t child = fork();
    if (child < 0) {
        std::perror("fork");
        return 4;
    }
    if (child == 0) {
        if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) _exit(120);
        if (prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) != 0) _exit(122);
        umask(0077);
        if (chdir("/") != 0) _exit(123);
        try {
            set_limit(RLIMIT_AS, 512ULL * 1024ULL * 1024ULL, 512ULL * 1024ULL * 1024ULL);
            set_limit(RLIMIT_CPU, 30, 30);
            set_limit(RLIMIT_NOFILE, 256, 256);
            set_limit(RLIMIT_NPROC, 64, 64);
        } catch (...) {
            _exit(121);
        }
        execl(executable.c_str(), executable.c_str(), "--capabilities", static_cast<char *>(nullptr));
        _exit(errno == ENOENT ? 127 : 126);
    }
    int status = 0;
    if (waitpid(child, &status, 0) < 0) {
        std::perror("waitpid");
        return 5;
    }
    if (WIFEXITED(status)) {
        std::cout << "service_exit=" << WEXITSTATUS(status) << "\n";
        return WEXITSTATUS(status);
    }
    if (WIFSIGNALED(status)) {
        std::cout << "service_signal=" << WTERMSIG(status) << "\n";
        return 128 + WTERMSIG(status);
    }
    return 6;
}
