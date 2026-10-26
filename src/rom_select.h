/*
 * rom_select.h - find a usable ROM folder before the runtime is started.
 */
#ifndef KOF97_ROM_SELECT_H
#define KOF97_ROM_SELECT_H

#include <stddef.h>

/* Fill `out` with a ROM directory when one can be discovered and the user did
 * not already pass --rom-path.  Returns 1 when `out` was set, 0 when nothing
 * was found (the runtime then uses its own default), and -1 on error. */
int kof97_maybe_select_rom(int argc, char **argv, char *out, size_t cap);

#endif
