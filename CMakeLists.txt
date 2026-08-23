cmake_minimum_required(VERSION 3.22)
project(etternhall_os VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

add_executable(eos-phone-shell
    src/eos-shell/main.cpp
)

target_link_libraries(eos-phone-shell PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)

add_executable(eos-init
    src/eos-init/main.cpp
)

add_executable(eos-serviced
    src/eos-core/eos-serviced.cpp
)

add_executable(eos-supervise
    src/eos-core/eos-supervise.cpp
)

add_executable(eos-assistantd
    src/eos-ai/eos-assistantd.cpp
)

add_executable(eos-inputd
    src/eos-input/eos-inputd.cpp
)

add_executable(eos-oobe
    src/eos-oobe/main.cpp
)
target_link_libraries(eos-oobe PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)

add_executable(eos-immersived
    src/eos-immersive/eos-immersived.cpp
)

target_compile_options(eos-phone-shell PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall;-Wextra;-Wpedantic>
)

install(TARGETS eos-phone-shell eos-init eos-serviced eos-supervise eos-assistantd eos-inputd eos-oobe eos-immersived RUNTIME DESTINATION bin)
