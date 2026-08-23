#include <cmath>
#include <iostream>
#include <string>

struct TouchPoint {
    double x;
    double y;
    long long timestamp_ms;
};

struct Gesture {
    std::string type;
    double dx;
    double dy;
    long long duration_ms;
};

static Gesture classify(const TouchPoint &start, const TouchPoint &end) {
    const double dx = end.x - start.x;
    const double dy = end.y - start.y;
    const double distance = std::sqrt(dx * dx + dy * dy);
    const long long duration = std::max(1LL, end.timestamp_ms - start.timestamp_ms);
    if (distance < 24.0) return {"tap", dx, dy, duration};
    if (std::abs(dx) > std::abs(dy) * 1.25) return {dx > 0 ? "swipe-right" : "swipe-left", dx, dy, duration};
    return {dy > 0 ? "swipe-down" : "swipe-up", dx, dy, duration};
}

static int emit_gesture(const TouchPoint &start, const TouchPoint &end, const std::string &display, const std::string &window) {
    const Gesture gesture = classify(start, end);
    const double speed = std::sqrt(gesture.dx * gesture.dx + gesture.dy * gesture.dy) / static_cast<double>(gesture.duration_ms);
    std::cout << "{\"schema\":\"eos-touch-0.2\",\"type\":\"gesture." << gesture.type
              << "\",\"phase\":\"end\",\"pointer_id\":1,\"position\":{\"x\":" << end.x
              << ",\"y\":" << end.y << "},\"start\":{\"x\":" << start.x << ",\"y\":" << start.y
              << "},\"delta\":{\"x\":" << gesture.dx << ",\"y\":" << gesture.dy
              << "},\"duration_ms\":" << gesture.duration_ms << ",\"speed\":" << speed
              << ",\"display_id\":\"" << display << "\",\"window_id\":\"" << window
              << "\",\"delivery\":\"eos-ipcd\"}\n";
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        const TouchPoint origin{100.0, 400.0, 0};
        const TouchPoint tap{101.0, 401.0, 80};
        const TouchPoint right{260.0, 402.0, 240};
        const TouchPoint up{101.0, 150.0, 260};
        std::cout << "protocol=eos-touch-0.2 input=normalized display=eos-displayd window=eos-windowd\n";
        emit_gesture(origin, tap, "internal-0", "notes-main");
        emit_gesture(origin, right, "internal-0", "notes-main");
        emit_gesture(origin, up, "internal-0", "notes-main");
        return 0;
    }
    if (argc == 12 && std::string(argv[1]) == "--gesture" && std::string(argv[8]) == "--display" && std::string(argv[10]) == "--window") {
        try {
            const TouchPoint start{std::stod(argv[2]), std::stod(argv[3]), std::stoll(argv[4])};
            const TouchPoint end{std::stod(argv[5]), std::stod(argv[6]), std::stoll(argv[7])};
            return emit_gesture(start, end, argv[9], argv[11]);
        } catch (...) {
            std::cerr << "eos-inputd error: invalid touch point\n";
            return 2;
        }
    }
    std::cout << "eos-inputd: protocol=eos-touch-0.2; use --self-test or --gesture x1 y1 t1 x2 y2 t2 --display id --window id\n";
    return 0;
}
