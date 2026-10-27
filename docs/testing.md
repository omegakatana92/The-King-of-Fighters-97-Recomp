# Testing and measured results

All numbers below are from the Windows Release build unless stated otherwise.
Commands are shown for PowerShell; on Linux replace `kof 97.exe` with
`build-linux/kof97` and use forward slashes.

## Environment

| Item | Version |
|---|---|
| Windows | Windows 11 x64 |
| Compiler | MSVC 19.51.36257 (Visual Studio 18 2026) |
| CMake | 4.3.3 |
| SDL2 | 2.32.10 |
| Linux build host | Ubuntu 22.04.5 under WSL2 |
| Linux compiler | gcc 11.4.0 |
| Linux CMake / SDL2 | 4.4.4 / 2.0.20 |

## 1. ROM validation

The archive is the MAME `kof97` MVS set. Every file's CRC-32 and SHA-1 was
computed from the zip and compared with `ROM_START( kof97 )` in MAME's
`src/mame/snk/neogeo.cpp`; all 13 match. The `NEO-GEO` signature is at `$100`
of the byte-swapped fixed bank, and the four header entry points are `JMP`
stubs. See `game-notes.md` for the table.

No decryption or patching is performed. The build reads the user's files
directly from `KOF97_ROM_DIR`.

## 2. Interpreted boot

```
"kof 97.exe" --headless --interp --rom-path roms-src --frames 4001 ^
    --screenshot 600:shots/ip-600.png --screenshot 1200:shots/ip-1200.png ^
    --screenshot 4000:shots/ip-4000.png
```

Result: real BIOS eye-catcher at frame 600, CHARACTERS RANKING at 1200,
title at 4000. This validates the board model independently of the
recompiler.

## 3. Native build and boot

```
cmake -S . -B build-windows -G "Visual Studio 18 2026" -A x64 ^
      -DKOF97_ROM_DIR=C:/.../roms-src ^
      -DSDL2_DIR=C:/.../SDL2-2.32.10/cmake
cmake --build build-windows --config Release --parallel
```

Recompiler output (static discovery only):

```
[m68krecomp] pointer scan: 26125 seeds
[m68krecomp] kof97: 1342074 instructions emitted across routines
[m68krecomp] 27691 routines, 41859 dispatch entries
```

Boot and attract:

```
"kof 97.exe" --headless --rom-path roms-src --frames 4001 ^
    --screenshot 300:shots/300.png --screenshot 600:shots/600.png ^
    --screenshot 1200:shots/1200.png --screenshot 2400:shots/2400.png ^
    --screenshot 4000:shots/4000.png
[exec] native blocks 1969670, native instructions 76336899,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

Screens checked: NEO-GEO eye-catcher (600), CHARACTERS RANKING (1200),
intro artwork (2400), title screen (4000).

## 4. Coin, menus and a match

```
"kof 97.exe" --headless --rom-path roms-src --frames 11001 ^
    --input tests/play.txt ^
    --screenshot 9600:shots/fight.png --screenshot 9900:shots/ko.png ^
    --screenshot 10700:shots/round2.png
```

Frames checked: HOW TO PLAY (4300), CHARACTER SELECT (5000), MODE SELECT
(6000), ORDER SELECT (7000), ROUND 1 (9000-9600), K.O. / PERFECT (9900),
next team member (10700).

Input responsiveness was checked separately: holding `down` at frame 9000
makes Kyo crouch by frame 9055, and the attack buttons produce the
corresponding animations.

## 5. Correctness: `--verify`

```
"kof 97.exe" --headless --verify --rom-path roms-src --frames 8001 ^
    --input tests/coin_start.txt
[verify] 6360574 blocks checked, 0 mismatches
[exec] native blocks 6360574, native instructions 146235444,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

An earlier run before the profile pass checked 6,360,110 blocks with 0
mismatches.

## 6. Coverage and the profile pass

Before profiling:

```
[attract, 6000 frames] interpreted 6420 (99.99% native), 54 uncovered
[play_long, 19000 frames] interpreted 494036 (99.86% native), 386 uncovered
```

Profile pass:

```
cmake --build build-windows --config Release --target profile
[exec] 54 new entry points ... entries.txt now lists 54
[exec] 386 new entry points ... entries.txt now lists 431
cmake --build build-windows --config Release --target kof97
```

After profiling:

```
[play_long, 19000 frames]
[exec] native blocks 14510162, native instructions 354889002,
       interpreted instructions 114 (100.00% native), 7 uncovered entry points

[audio_select, 12000 frames]
[exec] native blocks 9486483, native instructions 224333873,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

Final table: 42,461 dispatch entries, 1,358,361 instructions emitted. The 7
interpreted entries in the long run are RTC-seeded AI paths that vary between
runs; the audio-check and verify sessions are fully native.

## 7. Audio repair and regression check

### Before

```
./kof97 --headless --rom-path /home/deck/.local/share/kof97/roms \
  --frames 12001 --input tests/play_long.txt --wav before.wav
```

The 1 s RMS timeline had silent runs at 79-106 s (character select through
mode select) and 112-121 s (order select), with only the match audio from
121 s onward. `NG_AUDIO_TRACE=1` at frames 4000-7300 showed:

```
banks=0F000/0E000/0C000/08000  pc=012C  cmd=00
```

The runtime's bank formula added `0x10000`, so those selections read
`1F000/1E000/1C000/18000` — the wrong half of the 128 KB M1.

### After

The same capture after the fix is continuous from 83 s:

```
83-120 s: min RMS  1171.9  mean RMS  2589.0
120-170 s: min RMS   107.1  mean RMS  2298.9
170-200 s: min RMS   283.6  mean RMS  2273.1
PASS: continuous audio through character select and the match (peak 24752)
```

`--interp` with the same script gives the same continuous windows (min RMS
1072.0 / 102.3 / 293.0), confirming the fix is in the shared audio path.

A MAME 0.242 capture of the same coin/start sequence shows the same activity
pattern after allowing for a ~5 s boot-time offset: title music at 56-59 s
(ours) / 61-64 s (MAME), the same silent intro gap, and character-select BGM
from 83 s / 88 s.

Character-select button presses (`tests/audio_select.txt`) add five 50 ms
windows above 5112 RMS that are absent from the no-input run, i.e. voices and
selection effects are present on top of the BGM.

### Regression target

```
cmake --build build-linux --target audio-check
83-120 s: min RMS  1171.9  mean RMS  2589.0
120-170 s: min RMS   107.1  mean RMS  2298.9
170-200 s: min RMS   283.6  mean RMS  2273.1
PASS: continuous audio through character select and the match (peak 21498)
```

`tests/check_audio.py` uses only the Python standard library.

## 8. Native vs interpreter screenshots

The same input script was run with `--interp` and natively, and the PNGs were
compared by SHA-256.

| Frame | Screen | Result |
|---|---|---|
| 5000 | CHARACTER SELECT | byte-identical |
| 6000 | MODE SELECT | byte-identical |
| 4300 | HOW TO PLAY | differs by a scanline (raster palette change) |
| 8000 | match | differs by a scanline (raster palette change) |

The difference is host scheduling: `--interp` runs Musashi in cycle-budget
slices and can overshoot a scanline deadline, while recompiled code yields at
the event. `--verify` checks every native block against Musashi and reports 0
mismatches, so this is not a translation error.

## 9. Windows package

```
powershell -ExecutionPolicy Bypass -File scripts/package-windows.ps1
```

The package contains `kof 97.exe`, `SDL2.dll`, `vcruntime140.dll`,
`vcruntime140_1.dll`, `README.txt`, `Prepare-ROMs.ps1` and `LICENSES/`.
`dumpbin /dependents` shows only SDL2, dbghelp, the VC++ runtime and the
Windows UCRT API sets. The packaged exe was run headless from the package
folder and exited 0 with 100% native coverage.

Windowed launch: 300 frames with `--scale 1 --mute`, exit 0.

## 10. Linux and AppImage

Build host: Ubuntu 22.04.5 under WSL2, gcc 11.4.0, CMake 4.4.4, SDL2 2.0.20.
The Linux build regenerated the same 42,461-entry table (1,358,361
instructions) and reported 100.00% native on the audio and verify sessions:

```
[play_long, 19000 frames]
[exec] native blocks 14510162, native instructions 354889002,
       interpreted instructions 114 (100.00% native), 7 uncovered entry points

[audio_select, 12000 frames]
[exec] native blocks 9486483, native instructions 224333873,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

AppImage checks:

| Check | Result |
|---|---|
| Executable bit | set by the build script |
| Startup (FUSE mount) | runs |
| Startup (`APPIMAGE_EXTRACT_AND_RUN=1`) | runs |
| ROM discovery (`$HOME/.local/share/kof97/roms`) | runs without `--rom-path` |
| Headless run | 6000 frames, 100.00% native |
| Character-select audio | `check_audio.py` PASS; min RMS 1171.9 in 83-120 s |
| `--verify` (AppImage) | 2000 frames, 1,215,070 blocks, 0 mismatches |
| `--interp` (AppImage) | 2000 frames, runs |
| Fullscreen run | 300 frames under WSLg, exit 0 |
| Windowed run | 300 frames, exit 0 |
| SDL2 resolution | bundled `libSDL2-2.0.so.0`; all other libraries resolve from the system |
| Gamepad | SDL virtual-pad test passes on Windows; no physical pad under Linux |
| Size | 16,169,464 bytes |

The fixed AppImage is installed as
`/home/deck/Downloads/neo geo appimagesd/KOF97-AudioFixed-x86_64.AppImage`.
The original AppImage, the other games' AppImages and the ROM folder were
not modified.

`ldd` on the packaged binary shows the bundled SDL2 plus the expected system
libraries (libc, libstdc++, libm, X11/Wayland, PulseAudio/ALSA, gbm/drm). No
library is missing.

Physical Steam Deck hardware was not available, so Deck LCD/OLED, Gaming Mode
and Steam Input remain unverified. See `docs/compatibility.md`.

## 11. Toolkit tests

The vendored toolkit was configured as a top-level project and its CTest
suite run:

```
conformance: 59/60 68000 test programs pass recompiled (reference interpreter: 59/60)
gamepad: virtual pad is player 1
gamepad: virtual pad is player 2
gamepad: all checks pass
```

The gamepad test uses SDL's virtual joystick, so it checks the mapping and
hot-plug handling without a physical pad.

## Reproducing from scratch

```
# Windows
cmake -S . -B build-windows -G "Visual Studio 18 2026" -A x64 ^
      -DKOF97_ROM_DIR=C:/path/to/roms-src ^
      -DSDL2_DIR=C:/path/to/SDL2-2.32.10/cmake
cmake --build build-windows --config Release --parallel
cmake --build build-windows --config Release --target profile
cmake --build build-windows --config Release --target kof97
powershell -ExecutionPolicy Bypass -File scripts/package-windows.ps1

# Linux / AppImage
./scripts/build-linux.sh /path/to/roms-src
./packaging/appimage/build-appimage.sh /path/to/roms-src
```

The generated C, the entry list and the screenshots live only in the build
tree; they are never committed.
