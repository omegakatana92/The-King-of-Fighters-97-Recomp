cmake_minimum_required(VERSION 3.21)
project(kof97 VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# The neogeorecomp toolkit: the in-tree copy (a submodule in a clean
# checkout), or a checkout next to this project.
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/neogeorecomp/CMakeLists.txt)
    set(ng_default ${CMAKE_CURRENT_SOURCE_DIR}/neogeorecomp)
else()
    set(ng_default ${CMAKE_CURRENT_SOURCE_DIR}/../neogeorecomp)
endif()
set(NEOGEORECOMP_DIR ${ng_default} CACHE PATH "neogeorecomp checkout")
add_subdirectory(${NEOGEORECOMP_DIR} neogeorecomp_build)

# Your unzipped MAME "kof97" set and "neogeo" system ROMs.  The build reads
# them where they are; nothing derived from them is committed.
set(KOF97_ROM_DIR "" CACHE PATH "Directory with your kof97 and Neo Geo BIOS ROM files")
# Optional: entry points a previous run found at runtime (--dump-misses).
set(KOF97_ENTRIES "${CMAKE_BINARY_DIR}/entries.txt" CACHE FILEPATH "Extra entry points for the recompiler")

# Stage 1: the generator.
add_executable(kof97_recomp src/recomp_main.c src/game.c)
target_link_libraries(kof97_recomp PRIVATE m68krecomp_core)
target_include_directories(kof97_recomp PRIVATE src)

# Stage 2: the player, with the generated C when ROMs are available.
set(GAME_SOURCES src/main.c src/rom_select.c)
set(GEN_DIR ${CMAKE_BINARY_DIR}/generated)
set(GEN_FILES 16)
if(KOF97_ROM_DIR)
    set(GEN_SOURCES ${GEN_DIR}/recomp_table.c)
    math(EXPR last "${GEN_FILES} - 1")
    foreach(i RANGE ${last})
        if(i LESS 10)
            list(APPEND GEN_SOURCES ${GEN_DIR}/recomp_0${i}.c)
        else()
            list(APPEND GEN_SOURCES ${GEN_DIR}/recomp_${i}.c)
        endif()
    endforeach()
    # The entry list starts empty; the `profile` target fills it from a
    # scripted play session and the next build regenerates with it.
    if(NOT EXISTS ${KOF97_ENTRIES})
        file(WRITE ${KOF97_ENTRIES} "")
    endif()
    file(MAKE_DIRECTORY ${GEN_DIR})
    add_custom_command(
        OUTPUT ${GEN_SOURCES} ${GEN_DIR}/recomp_common.h
        COMMAND kof97_recomp --rom-path ${KOF97_ROM_DIR} --out ${GEN_DIR} --files ${GEN_FILES}
                --entries ${KOF97_ENTRIES}
        DEPENDS kof97_recomp ${KOF97_ENTRIES}
        COMMENT "Recompiling The King of Fighters '97 from ${KOF97_ROM_DIR}")
    list(APPEND GAME_SOURCES ${GEN_SOURCES})
endif()

add_executable(kof97 ${GAME_SOURCES} src/game.c)
if(WIN32)
    set_target_properties(kof97 PROPERTIES OUTPUT_NAME "kof 97")
else()
    set_target_properties(kof97 PROPERTIES OUTPUT_NAME "kof97")
endif()
target_link_libraries(kof97 PRIVATE neogeorecomp)
target_include_directories(kof97 PRIVATE src ${GEN_DIR})
if(KOF97_ROM_DIR)
    add_custom_target(profile
        COMMAND kof97 --headless --rom-path ${KOF97_ROM_DIR} --frames 6000
                --dump-misses ${KOF97_ENTRIES}
        COMMAND kof97 --headless --rom-path ${KOF97_ROM_DIR} --frames 19000
                --input ${CMAKE_CURRENT_SOURCE_DIR}/tests/play_long.txt
                --dump-misses ${KOF97_ENTRIES}
        DEPENDS kof97
        COMMENT "Profiling scripted sessions for runtime-only entry points")
    target_compile_definitions(kof97 PRIVATE KOF97_HAVE_RECOMP)
    if(MSVC)
        # Generated routines are large; /bigobj lifts the section limit.
        # /O1 avoids MSVC's superlinear optimizer blow-up on these giant
        # dispatch functions and still runs the 68000 code at full speed.
        set_source_files_properties(${GEN_SOURCES} PROPERTIES COMPILE_OPTIONS "/bigobj;/O1")
    else()
        # GCC/Clang at -O3 spend a very long time on these giant switch
        # functions.  -O1 keeps the build practical and the generated code is
        # already one C block per instruction, so little is lost at runtime.
        set_source_files_properties(${GEN_SOURCES} PROPERTIES COMPILE_OPTIONS "-O1")
    endif()
endif()
if(MSVC)
    target_compile_definitions(kof97 PRIVATE _CRT_SECURE_NO_WARNINGS)
    target_compile_definitions(kof97_recomp PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

# Ship the SDL2 DLL (when the window is built) next to the executable.
if(WIN32 AND TARGET SDL2::SDL2)
    add_custom_command(TARGET kof97 POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_RUNTIME_DLLS:kof97> $<TARGET_FILE_DIR:kof97>
        COMMAND_EXPAND_LISTS)
endif()
