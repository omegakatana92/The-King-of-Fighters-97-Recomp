# Generic changes in the vendored toolkit

`neogeorecomp/` is upstream **v0.2.0**, commit
`af96b2b4b39b42b392b17bcaa6a74a5f27088202` (`toolkit.ref`), plus the changes
below. None of them contains game addresses, ROM data or title-specific
branches; each is a hardware-model or host fix that any game can use. They are
released under the toolkit's MIT license.

## Sprite region rounded up and zero-filled (new in this port)

`src/video.c`, `decode_sprites()`.

The LSPC masks sprite tile numbers to the next power of two because the
address lines above the fitted C ROMs are not connected. The old code
allocated exactly `tiles * 256` bytes but still used the power-of-two mask.
For a C ROM whose size is not a power of two this lets a tile number reach
past the allocation.

KOF '97 has 40 MB of C ROM (32 MB would be the next power of two down), so
during the BIOS boot a sprite fetch with a high tile number read past the
heap and crashed the process at about frame 126. The fix allocates the
rounded-up tile count with `calloc`, so the tail reads as zero, matching
MAME's `neosprite_optimized_device`, which rounds the sprite region up and
zero-fills it. Games with power-of-two C ROMs are unaffected.

## MVS watchdog

`src/neogeo.c`, `src/io.c`, `src/ng_internal.h`.

MAME resets the board 3,244,030 master clocks (1,622,015 68000 clocks) after
the last write to `$300001`. Some late carts use the watchdog as a protection
check: if the reset does not happen, they set a failure flag. The runtime now
models the deadline, the kick (including the `$300001` mirror), and a reset
that restarts the 68k from the BIOS vectors while keeping work and backup RAM.

## Non-linear program banking and NEO-SMA support

`include/neogeorecomp/neogeo.h`, `src/bus.c`, `src/exec.c`.

`ng_game_t` gained an optional `ng_bank_map_t` (offset table plus selector
bit list), a bank-select port override, a protection read address/value and
two NEO-SMA LFSR read addresses. Carts that leave them zero use the standard
linear 1 MB banking. KOF '97 uses the default path; the fields exist for the
later NEO-SMA carts.

The dispatcher also refuses to run native code from the `$200000` window when
`ng_bank_base != 0`, because the same 68k address then refers to different
bytes. Such code is interpreted until the window returns to bank 0.

## Fixed-layer banking selectors

`src/video.c`, `include/neogeorecomp/neogeo.h`.

`NG_FIX_BANK_GAROU` and `NG_FIX_BANK_KOF2000` implement the two VRAM bank
schemes used by S ROMs larger than 128 KB. KOF '97 has a plain 128 KB S ROM
and selects `NG_FIX_BANK_NONE`.

## Fullscreen with 4:3 pillarboxing

`src/window_sdl.c`, `src/neogeo.c`, `src/platform.c`.

`--fullscreen` creates a desktop-fullscreen window, and the 320x224 image is
scaled to a 4:3 rectangle centred in the output with black bars. It is never
stretched to 16:10. F11 toggles the mode. This is what the Steam Deck AppRun
passes by default.

## Z80 bank window base and masks

`src/audio.c`.

MAME's `init_audio()` places banked M1 windows at `0x10000 + ...`, above the
fixed 64 KB at the bottom of the M1, and masks the bank register to the ROM
size. The old code used the raw bank value as an offset. The fix follows
MAME; it matters for drivers that bank the upper part of a 128 KB M1, as
KOF '97's does.

## Native instruction accounting

`src/exec.c`.

The `[exec]` report now counts native instructions and prints a coverage
percentage next to the interpreted count, so coverage is measured rather than
estimated.

## Audio diagnostics

`src/audio.c`, `src/ym2610.cpp`.

`NG_AUDIO_TRACE=1` prints command latches, ROM selection and Z80 state every
60 frames. Off by default; useful when bringing up a new sound driver.
