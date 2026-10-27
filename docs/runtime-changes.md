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

## M1 bank mask from the M1 file size (`src/audio.c`)

MAME's `init_audio()` builds each Z80 bank entry as

```
bank_address = 0x10000 + ((bank << (11 + window)) & address_mask);
```

in the audio region. `ROM_RELOAD` places the first byte of the M1 file at
region offset `0x10000`, so the **file** offset is the masked value alone.
`address_mask` comes from the region length (`M1 size + 0x10000`); for files
up to 512 KB that is `(M1 size - 1) & 0x3FFFF`.

The vendored code used `0x10000 + (bank & (size - 0x10000 - 1))`, which for a
128 KB M1 rotates every bank by `+0x10000`. KOF '97 selects banks
`0x08000`-`0x0F000` at character select; the runtime read
`0x18000`-`0x1F000` instead, so the driver loaded the wrong music data and the
BGM went silent while 68000-triggered ADPCM effects kept playing. The same
failure appears in `--interp` because the audio path is shared.

The fix uses the M1 file size, as MAME does:

```c
off = (bank & ((size - 1) & 0x3FFFF)) + (a & window_mask);
```

This is generic for 64 KB, 128 KB, 256 KB and 512 KB M1s.

Evidence: `NG_AUDIO_TRACE=1` showed banks `0F000/0E000/0C000/08000` during
the silent character-select section; a MAME 0.242 capture of the same
coin/start sequence has music there (allowing for a ~5 s boot-time offset).
After the fix the WAV is continuous from 83 s through the match.

## Frame-boundary Z80 sync (`src/audio.c`)

`audio_take_samples()` now calls `audio_sync()` before generating samples.
The Z80 previously advanced only when the 68000 touched the sound latches, so
a game that stopped polling could starve the sound CPU and its YM2610 timers.
Syncing once per frame keeps the Z80 in step with `ng_cycles` regardless of
68k polling. This is generic and does not alter the 68000 timeline.

## Audio regression check (`tests/check_audio.py`, `audio-check`)

The `audio-check` target runs a 12,000-frame coin/start session, writes
`build-*/audio-check.wav`, and checks every 1 s window from 83 s to 200 s.
Before the fix the 83-120 s character-select window was almost entirely
silent; after it the minimum RMS is 1171.9 in that window and 107.1 across
the match. The check is dependency-free (Python standard library only).

## Native instruction accounting

`src/exec.c`.

The `[exec]` report now counts native instructions and prints a coverage
percentage next to the interpreted count, so coverage is measured rather than
estimated.

## Audio diagnostics

`src/audio.c`, `src/ym2610.cpp`.

`NG_AUDIO_TRACE=1` prints command latches, ROM selection and Z80 state every
60 frames. Off by default; useful when bringing up a new sound driver.
