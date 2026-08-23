#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

static bool safe_route(const std::string &route) {
    return !route.empty() && route.find("..") == std::string::npos && route.find('/') == std::string::npos && route.find('\\') == std::string::npos;
}

static bool explicit_root(const std::string &root) {
    return !root.empty() && root.rfind('/', 0) == 0 && root.find("..") == std::string::npos;
}

static fs::path state_path(const fs::path &root) {
    return root / "activities" / "stack.json";
}

static std::vector<std::string> read_stack(const fs::path &path) {
    std::vector<std::string> stack;
    std::ifstream input(path);
    std::string line;
    bool inside_stack = false;
    while (std::getline(input, line)) {
        if (line.find("\"stack\": [") != std::string::npos) {
            inside_stack = true;
            continue;
        }
        if (inside_stack && line.find(']') != std::string::npos) {
            break;
        }
        if (inside_stack) {
            const auto begin = line.find('"');
            const auto end = line.find('"', begin + 1);
            if (begin != std::string::npos && end != std::string::npos && end > begin + 1) {
                stack.push_back(line.substr(begin + 1, end - begin - 1));
            }
        }
    }
    return stack;
}

static bool write_stack(const fs::path &path, const std::vector<std::string> &stack) {
    std::error_code error;
    fs::create_directories(path.parent_path(), error);
    if (error) return false;
    const auto temporary = path.string() + ".tmp";
    std::ofstream output(temporary, std::ios::trunc);
    if (!output) return false;
    output << "{\n  \"schema\": \"eos-activity-stack-0.1\",\n  \"active\": \"" << (stack.empty() ? "" : stack.back()) << "\",\n  \"stack\": [\n";
    for (std::size_t index = 0; index < stack.size(); ++index) {
        output << "    \"" << stack[index] << "\"" << (index + 1 == stack.size() ? "\n" : ",\n");
    }
    output << "  ]\n}\n";
    output.flush();
    if (!output) return false;
    fs::rename(temporary, path, error);
    if (error) {
        fs::remove(temporary);
        return false;
    }
    return true;
}

static void lifecycle(const std::string &activity, const std::string &state) {
    std::cout << "eos-activity-0.1 lifecycle=" << state << " activity=" << activity << "\n";
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "protocol=eos-activity-0.1 manager=eos-activityd\n";
        std::cout << "main=declared navigation=stack lifecycle=created,started,resumed,paused,stopped,destroyed\n";
        std::cout << "events=touch,swipe,ui-action delivery=active-activity-only restore=atomic\n";
        return 0;
    }
    if (argc == 5 && std::string(argv[1]) == "--launch" && std::string(argv[3]) == "--root" && explicit_root(argv[4])) {
        const std::string route = argv[2];
        if (!safe_route(route)) return 2;
        const fs::path root = argv[4];
        const auto path = state_path(root);
        const auto stack = std::vector<std::string>{route};
        if (!write_stack(path, stack)) return 3;
        lifecycle(route, "created");
        lifecycle(route, "started");
        lifecycle(route, "resumed");
        std::cout << "navigation=launch active=" << route << " stack=1\n";
        return 0;
    }
    if (argc == 5 && std::string(argv[1]) == "--push" && std::string(argv[3]) == "--root" && explicit_root(argv[4])) {
        const std::string route = argv[2];
        if (!safe_route(route)) return 2;
        const fs::path path = state_path(argv[4]);
        auto stack = read_stack(path);
        if (stack.empty()) return 3;
        lifecycle(stack.back(), "paused");
        stack.push_back(route);
        if (!write_stack(path, stack)) return 3;
        lifecycle(route, "created");
        lifecycle(route, "started");
        lifecycle(route, "resumed");
        std::cout << "navigation=push active=" << route << " stack=" << stack.size() << "\n";
        return 0;
    }
    if (argc == 4 && std::string(argv[1]) == "--back" && std::string(argv[2]) == "--root" && explicit_root(argv[3])) {
        const fs::path path = state_path(argv[3]);
        auto stack = read_stack(path);
        if (stack.empty()) return 3;
        const std::string closing = stack.back();
        if (stack.size() == 1) {
            lifecycle(closing, "paused");
            lifecycle(closing, "stopped");
            lifecycle(closing, "destroyed");
            stack.clear();
        } else {
            lifecycle(closing, "paused");
            lifecycle(closing, "stopped");
            lifecycle(closing, "destroyed");
            stack.pop_back();
            lifecycle(stack.back(), "resumed");
        }
        if (!write_stack(path, stack)) return 3;
        std::cout << "navigation=back active=" << (stack.empty() ? "none" : stack.back()) << " stack=" << stack.size() << "\n";
        return 0;
    }
    if (argc == 4 && std::string(argv[1]) == "--restore" && std::string(argv[2]) == "--root" && explicit_root(argv[3])) {
        const auto stack = read_stack(state_path(argv[3]));
        std::cout << "restore=activity-stack active=" << (stack.empty() ? "none" : stack.back()) << " stack=" << stack.size() << "\n";
        return 0;
    }
    std::cout << "eos-activityd: protocol eos-activity-0.1; use --self-test, --launch route --root path, --push route --root path, --back --root path or --restore --root path\n";
    return 0;
}
