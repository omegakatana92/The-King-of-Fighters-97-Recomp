/*
 * rom_select.c - locate the user's ROM folder without a dialog.
 *
 * Order: KOF97_ROM_DIR, "roms" in the working directory, "roms" beside the
 * executable, then the per-user data folder.  A candidate is accepted only if
 * it holds the game's first program ROM, so a stray empty directory cannot
 * shadow a good one.  An explicit --rom-path always wins.
 */
#include "rom_select.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

#define ROM_PROBE "232-p1.p1"

static int has_roms(const char *dir) {
    char path[4096 + 16];
    if (!dir || !*dir) return 0;
    snprintf(path, sizeof(path), "%s/%s", dir, ROM_PROBE);
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    fclose(f);
    return 1;
}

static int exe_dir(char *out, size_t cap) {
#ifdef _WIN32
    DWORD n = GetModuleFileNameA(NULL, out, (DWORD)cap);
    if (n == 0 || n >= cap) return 0;
    char *slash = strrchr(out, '\\');
    if (!slash) slash = strrchr(out, '/');
    if (!slash) return 0;
    *slash = '\0';
    return 1;
#else
    ssize_t n = readlink("/proc/self/exe", out, cap - 1);
    if (n <= 0) return 0;
    out[n] = '\0';
    char *slash = strrchr(out, '/');
    if (!slash) return 0;
    *slash = '\0';
    return 1;
#endif
}

static int user_data_dir(char *out, size_t cap) {
#ifdef _WIN32
    const char *base = getenv("LOCALAPPDATA");
    if (!base || !*base) return 0;
    snprintf(out, cap, "%s/KOF97/roms", base);
    return 1;
#elif defined(__APPLE__)
    const char *home = getenv("HOME");
    if (!home || !*home) return 0;
    snprintf(out, cap, "%s/Library/Application Support/KOF97/roms", home);
    return 1;
#else
    const char *xdg = getenv("XDG_DATA_HOME");
    const char *home = getenv("HOME");
    if (xdg && *xdg) snprintf(out, cap, "%s/kof97/roms", xdg);
    else if (home && *home) snprintf(out, cap, "%s/.local/share/kof97/roms", home);
    else return 0;
    return 1;
#endif
}

int kof97_maybe_select_rom(int argc, char **argv, char *out, size_t cap) {
    for (int i = 1; i < argc; i++)
        if (!strcmp(argv[i], "--rom-path")) return 0;   /* explicit */

    const char *env = getenv("KOF97_ROM_DIR");
    if (has_roms(env)) {
        snprintf(out, cap, "%s", env);
        return 1;
    }

    if (has_roms("roms")) {
        snprintf(out, cap, "roms");
        return 1;
    }

    char dir[4096], cand[4096 + 16];
    if (exe_dir(dir, sizeof(dir))) {
        snprintf(cand, sizeof(cand), "%s/roms", dir);
        if (has_roms(cand)) { snprintf(out, cap, "%s", cand); return 1; }
    }

    if (user_data_dir(cand, sizeof(cand)) && has_roms(cand)) {
        snprintf(out, cap, "%s", cand);
        return 1;
    }

    return 0;
}
