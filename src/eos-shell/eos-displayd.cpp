#include <iostream>
#include <string>

struct DisplayProfile {
    int width;
    int height;
    int notch_top;
    std::string orientation;
};

static DisplayProfile profile(const std::string &orientation) {
    if (orientation == "landscape") return {2400, 1080, 80, orientation};
    return {1080, 2400, 80, "portrait"};
}

static bool safe_area(const DisplayProfile &display, double x, double y) {
    return !(display.orientation == "portrait" && y < display.notch_top);
}

int main(int argc, char **argv) {
    if (argc == 2 && std::string(argv[1]) == "--self-test") {
        std::cout << "protocol=eos-display-0.2 manager=eos-displayd\n";
        std::cout << "display=internal-0 portrait=1080x2400 landscape=2400x1080\n";
        std::cout << "safe-insets=0,80,0,0 notch=reserved orientation=policy-controlled\n";
        std::cout << "touch-space=logical input=eos-inputd window=eos-windowd vsync=managed\n";
        return 0;
    }
    if (argc == 6 && std::string(argv[1]) == "--transform" && std::string(argv[4]) == "--orientation") {
        try {
            const double raw_x = std::stod(argv[2]);
            const double raw_y = std::stod(argv[3]);
            const DisplayProfile display = profile(argv[5]);
            double x = raw_x;
            double y = raw_y;
            if (display.orientation == "landscape") {
                x = raw_y;
                y = 1080.0 - raw_x;
            }
            std::cout << "{\"schema\":\"eos-display-0.2\",\"display_id\":\"internal-0\",\"orientation\":\""
                      << display.orientation << "\",\"logical_size\":\"" << display.width << "x" << display.height
                      << "\",\"position\":{\"x\":" << x << ",\"y\":" << y << "},\"safe_area\":"
                      << (safe_area(display, x, y) ? "true" : "false") << "}\n";
            return 0;
        } catch (...) {
            std::cerr << "eos-displayd error: invalid coordinate or orientation\n";
            return 2;
        }
    }
    std::cout << "eos-displayd: protocol eos-display-0.2; use --self-test or --transform x y --orientation portrait|landscape\n";
    return 0;
}
