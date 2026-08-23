#include <cmath>
#include <iostream>
#include <string>

struct TouchPoint {
    double x;
    double y;
    long long timestamp_ms;
};

static std::string classify(const TouchPoint &start, const TouchPoint &end) {
    const double dx = end.x - start.x;
    const double dy = end.y - start.y;
    const double distance = std::sqrt(dx * dx + dy * dy);
    if (distance < 24.0) return "tap";
    if (std::abs(dx) > std::abs(dy) * 1.25) return dx > 0 ? "swipe-right" : "swipe-left";
    return dy > 0 ? "swipe-down" : "swipe-up";
}

int main(int argc, char **argv) {
    const bool self_test = argc > 1 && std::string(argv[1]) == "--self-test";
    if (!self_test) {
        std::cout << "eos-inputd: protocol=eos-touch-0.1 device=auto state=ready\n";
        return 0;
    }
    const TouchPoint origin{100.0, 400.0, 0};
    const TouchPoint tap{101.0, 401.0, 80};
    const TouchPoint right{260.0, 402.0, 240};
    const TouchPoint up{101.0, 150.0, 260};
    std::cout << "protocol=eos-touch-0.1\n";
    std::cout << "gesture-1=" << classify(origin, tap) << "\n";
    std::cout << "gesture-2=" << classify(origin, right) << "\n";
    std::cout << "gesture-3=" << classify(origin, up) << "\n";
    return 0;
}
