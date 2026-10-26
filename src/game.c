/*
 * game.c - The King of Fighters '97 (MAME set "kof97"), the verified ROM
 * layout shared by the player and the recompiler.
 *
 * The supplied set is SNK's original, unencrypted MVS release.  Layout and
 * CRCs were checked against MAME's neogeo.cpp ROM_START( kof97 ):
 *
 *   232-p1.p1    1 MB   fixed program bank, stored byte-swapped
 *   232-p2.sp2   4 MB   banked program image, stored byte-swapped
 *   232-s1.s1  128 KB   fixed layer
 *   232-m1.m1  128 KB   Z80 sound program
 *   232-c1..c6         sprite bitplanes, C1/C2 and C3/C4 8 MB, C5/C6 4 MB
 *   232-v1..v3   4 MB each   ADPCM-A samples
 *
 * The cart uses the standard Neo Geo bank selector at $2FFFF0: the low three
 * bits choose a 1 MB window inside the 4 MB banked image (MAME
 * neogeo_base_state::write_banksel).  There is no protection chip, no
 * encryption and no S ROM banking, so the generic toolkit path is used.
 */
#include "game.h"

const ng_game_t k_kof97 = {
    .name = "kof97",
    .title = "The King of Fighters '97",
    .prom_size = 0x500000,          /* 1 MB fixed + 4 MB banked */
    .prom = {
        {"232-p1.p1",  0x000000, 0x000000, 0x100000, 1},
        {"232-p2.sp2", 0x000000, 0x100000, 0x400000, 1},
    },
    .crom_size = 0x2800000,         /* 40 MB after pairing */
    .crom_pairs = {
        {"232-c1.c1", "232-c2.c2"},
        {"232-c3.c3", "232-c4.c4"},
        {"232-c5.c5", "232-c6.c6"},
    },
    .srom = "232-s1.s1",
    .m1 = "232-m1.m1",
    .vrom = {"232-v1.v1", "232-v2.v2", "232-v3.v3"},
};
