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
target_link_libraries(eos-phone-shell PRIVATE Qt6::Widgets)

add_executable(eos-windowd
    src/eos-shell/eos-windowd.cpp
)

add_executable(eos-displayd
    src/eos-shell/eos-displayd.cpp
)


add_executable(eos-init
    src/eos-init/main.cpp
)

add_executable(eos-serviced
    src/eos-core/eos-serviced.cpp
)

add_executable(eos-logd
    src/eos-core/eos-logd.cpp
)
target_link_libraries(eos-logd PRIVATE Qt6::Core)

add_executable(eos-storaged
    src/eos-core/eos-storaged.cpp
)
target_link_libraries(eos-storaged PRIVATE Qt6::Core)

add_executable(eos-sessiond
    src/eos-core/eos-sessiond.cpp
)
target_link_libraries(eos-sessiond PRIVATE Qt6::Core)

add_executable(eos-supervise
    src/eos-core/eos-supervise.cpp
)

add_executable(eos-assistantd
    src/eos-ai/eos-assistantd.cpp
)

add_executable(eos-audiod
    src/eos-ai/eos-audiod.cpp
)

add_executable(eos-modeld
    src/eos-ai/eos-modeld.cpp
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

add_executable(eos-browserd
    src/eos-browser/eos-browserd.cpp
)

add_executable(eos-mediad
    src/eos-media/eos-mediad.cpp
)

add_executable(eos-launcherd
    src/eos-launcher/eos-launcherd.cpp
)

add_executable(eos-marketd
    src/eos-launcher/eos-marketd.cpp
)

add_executable(eos-photod
    src/eos-photo/eos-photod.cpp
)

add_executable(eos-blinked
    src/eos-notify/eos-blinked.cpp
)

add_executable(eos-policyd
    src/eos-security/eos-policyd.cpp
)

target_compile_options(eos-phone-shell PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall;-Wextra;-Wpedantic>
)

install(TARGETS eos-phone-shell eos-windowd eos-displayd eos-init eos-serviced eos-logd eos-storaged eos-sessiond eos-supervise eos-assistantd eos-audiod eos-modeld eos-inputd eos-oobe eos-immersived eos-browserd eos-mediad eos-launcherd eos-marketd eos-photod eos-blinked eos-policyd RUNTIME DESTINATION bin)
