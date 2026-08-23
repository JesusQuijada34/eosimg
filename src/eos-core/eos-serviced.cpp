#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>

struct Service {
    std::string name;
    std::vector<std::string> dependencies;
};

static void visit(const std::string &name,
                  const std::map<std::string, Service> &services,
                  std::set<std::string> &temporary,
                  std::set<std::string> &permanent,
                  std::vector<std::string> &order) {
    if (permanent.contains(name)) return;
    if (temporary.contains(name)) throw std::runtime_error("service dependency cycle at " + name);
    auto found = services.find(name);
    if (found == services.end()) throw std::runtime_error("unknown service dependency " + name);
    temporary.insert(name);
    for (const auto &dependency : found->second.dependencies) {
        visit(dependency, services, temporary, permanent, order);
    }
    temporary.erase(name);
    permanent.insert(name);
    order.push_back(name);
}

int main(int argc, char **argv) {
    const bool dry_run = argc > 1 && std::string(argv[1]) == "--dry-run";
    const std::map<std::string, Service> services = {
        {"eos-logd", {"eos-logd", {}}},
        {"eos-powerd", {"eos-powerd", {"eos-logd"}}},
        {"eos-storaged", {"eos-storaged", {"eos-logd"}}},
        {"eos-packaged", {"eos-packaged", {"eos-logd", "eos-storaged"}}},
        {"eos-displayd", {"eos-displayd", {"eos-logd", "eos-powerd"}}},
        {"eos-windowd", {"eos-windowd", {"eos-displayd"}}},
        {"eos-phone-shell", {"eos-phone-shell", {"eos-windowd", "eos-packaged"}}},
    };
    try {
        std::set<std::string> temporary;
        std::set<std::string> permanent;
        std::vector<std::string> order;
        visit("eos-phone-shell", services, temporary, permanent, order);
        std::cout << "[eos-serviced] mode=" << (dry_run ? "dry-run" : "plan-only") << "\n";
        for (const auto &service : order) {
            std::cout << "[eos-serviced] start " << service << "\n";
        }
        return 0;
    } catch (const std::exception &error) {
        std::cerr << "[eos-serviced] error: " << error.what() << "\n";
        return 2;
    }
}
