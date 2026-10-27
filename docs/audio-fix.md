# KOF '97 audio repair (v0.1.1)

## Symptom

The game booted, the title/intro audio played, but the background music went
silent at the character-selection screen. Character voices and 68000-triggered
ADPCM sound effects could still be heard; the match music returned once the
fight started. The same silence occurred with `--interp`, so the fault was in
the shared audio path, not the recompiler.

## Root cause

The Z80 M1 bank window added `0x10000` to every bank offset:

```c
off = 0x10000 + ((s_bank[w] & reg_mask) + (a & win_mask[w]));
```

MAME's `init_audio()` builds each bank entry as
`0x10000 + ((bank << (11 + window)) & address_mask)` **in the audio region**.
`ROM_RELOAD` puts the first byte of the M1 file at region offset `0x10000`, so
the file offset is the masked value alone. For a 128 KB M1 the mask is
`0x1FFFF`.

KOF '97 selects banks `0x08000`-`0x0F000` at character select. The runtime's
extra `0x10000` rotated those to `0x18000`-`0x1F000`, so the Z80 driver read
the wrong half of its music data. At the match the driver selects
`0x18000`-`0x1F000`, which the broken formula happened to map correctly —
hence music worked in combat and not in the menus.

This is the same class of bug fixed in the KOF '96 port. That fix documents
MAME's formula and the character-select bank range; the KOF '97 vendored copy
still had the older variant with the extra `0x10000`.

## Evidence

`NG_AUDIO_TRACE=1` during the silent section (frames 4000-7300):

```
[audio] f=5040 pc=012C bios=0 banks=0F000/0E000/0C000/08000 cmd=00 rpy=23
[audio] f=6000 pc=013A bios=0 banks=0F000/0E000/0C000/08000 cmd=00 rpy=23
```

The driver is running (PC changes, reply latch updates), but the bank window
reads the wrong data.

Before the fix, the 1 s RMS timeline of a 12,000-frame capture:

```
silent runs (rms<20): ... (79.0, 106.0), (112.0, 121.0)
```

After the fix:

```
83-120 s: min RMS 1171.9  mean 2589.0
120-170 s: min RMS  107.1  mean 2298.9
170-200 s: min RMS  283.6  mean 2273.1
PASS: continuous audio through character select and the match
```

The interpreter capture has the same continuous windows (min 1072.0 / 102.3
/ 293.0).

MAME 0.242, same coin/start sequence, shows the same pattern after allowing
for a ~5 s boot-time offset: title music at 56-59 s (ours) / 61-64 s (MAME),
the same silent intro gap, and character-select BGM from 83 s / 88 s.

Character-select button presses add five 50 ms windows above 5112 RMS that
are absent from the no-input run, so voices and selection effects are present
on top of the BGM. The 280-290 s gap in the 19,000-frame capture is the
CONTINUE countdown; the ranking music resumes afterwards.

## Fix

`neogeorecomp/src/audio.c`:

```c
static const uint32_t win_mask[4] = {0x7FF, 0xFFF, 0x1FFF, 0x3FFF};
uint32_t reg_mask = size ? (((uint32_t)size - 1u) & 0x3FFFFu) : 0;
uint32_t off;
if (a >= 0xF000) off = (s_bank[0] & reg_mask) + (a & win_mask[0]);
else if (a >= 0xE000) off = (s_bank[1] & reg_mask) + (a & win_mask[1]);
else if (a >= 0xC000) off = (s_bank[2] & reg_mask) + (a & win_mask[2]);
else off = (s_bank[3] & reg_mask) + (a & win_mask[3]);
return r[off % size];
```

`audio_take_samples()` also calls `audio_sync()` before generating samples so
the Z80 and YM2610 timers keep running when the 68000 stops polling the sound
latches. Both changes are generic; no game addresses or ROM patches were
added.

## Files changed

- `neogeorecomp/src/audio.c` — M1 bank mask and frame-boundary sync.
- `tests/check_audio.py` — audio continuity regression (standard library only).
- `tests/audio_select.txt` — character-select inputs for voice/SFX checks.
- `CMakeLists.txt` — `audio-check` target, profile pass includes the select
  script, version 0.1.1.
- `README.md`, `docs/runtime-changes.md`, `docs/testing.md`,
  `docs/compatibility.md` — updated results and explanation.

## Build and test

```bash
cmake -S . -B build-linux -DCMAKE_BUILD_TYPE=Release \
      -DKOF97_ROM_DIR=/home/deck/.local/share/kof97/roms
cmake --build build-linux --parallel "$(nproc)"
cmake --build build-linux --target audio-check
```

Measured on the Linux/Steam Deck build:

| Check | Result |
|---|---|
| `audio-check` (12,000 frames) | PASS; 83-120 s min RMS 1171.9 |
| `--verify` (6,000 frames) | 4,775,936 blocks, 0 mismatches |
| Native coverage, audio-check | 100.00%, 0 interpreted |
| Native coverage, 19,000-frame play | 100.00% rounded, 114 interpreted / 7 uncovered (RTC-dependent) |
| AppImage `--verify` | 1,215,070 blocks, 0 mismatches |
| AppImage fullscreen | 300 frames, exit 0 |
| AppImage auto ROM discovery | works from `$HOME/.local/share/kof97/roms` |

Final AppImage:
`/home/deck/Downloads/neo geo appimagesd/KOF97-AudioFixed-x86_64.AppImage`.

## Remaining issues

- Physical Steam Deck LCD/OLED, Steam Input and Gaming Mode were not available;
  the AppImage was validated under WSL2 with WSLg.
- Audio was measured (RMS, spectrograms, MAME reference), not subjectively
  auditioned.
- A few RTC-seeded AI paths can fall back to Musashi in long runs; they are
  correct and negligible (114 of 354,889,002 instructions).
- The CONTINUE countdown is intentionally silent.
