# The King of Fighters '97 - native static recompilation

**The King of Fighters '97 (SNK, 1997 / MAME set `kof97`) running as a native
PC program: its 68000 program is translated ahead of time into C and executed
against a model of the MVS board by
[neogeorecomp](https://github.com/sp00nznet/neogeorecomp).**

Two deliverables are produced:

| Platform | Artifact |
|---|---|
| Windows x64 | `dist/windows/The-King-of-Fighters-97-Windows-x64/kof 97.exe` |
| Steam Deck / Linux x86_64 | `dist/steamdeck/kof97-SteamDeck-x86_64.AppImage` |

The game's own code runs natively. The real MVS system ROM boots the board,
checks its checksum and RAM, shows the SNK eye-catcher, handles coins and
credits, and calls the cartridge exactly as on hardware. There is no BIOS HLE
and no emulator frontend. The Musashi interpreter remains as the correctness
oracle and as the fallback for any code the flat dispatch cannot identify
(measured below).

> **No game data here.** You need your own legally obtained dumps of the MAME
> `kof97` set and the `neogeo` system ROMs. The recompiled C is generated from
> your dump on your machine into `build-*/`; it is never committed or
> distributed.

## Status

**v0.1.0, alpha - boots, runs attract mode and reaches a playable match on
100% recompiled code.**

| Area | State |
|---|---|
| Boot | Real MVS BIOS (`sp-s2.sp1`) -> eye-catcher -> character ranking -> intro -> title -> HOW TO PLAY -> CHARACTER SELECT -> MODE SELECT -> ORDER SELECT -> match |
| ROM set | Exact MAME `kof97` MVS set, all 13 files CRC-verified (see below) |
| Input / credits | Coin, Start, directions, A/B/C/D exercised through the BIOS, menus and a match |
| Gameplay | Team match reached and controlled: walking, all four attack buttons, KO and the next team member entering; CPU opponent fights back |
| Graphics | Sprites, backgrounds, palettes, fixed layer, raster effects |
| Audio | Z80 driver and YM2610 produce signal (3000-frame WAV: peak 11615, RMS 744, 51 of 202 half-second windows active); subjective mix not auditioned |
| Native coverage | **100.00%** of a 19,000-frame scripted session and **100.00%** of a 6,000-frame no-input attract session, after one profile pass; 0 uncovered entry points |
| `--verify` | 6,360,574 blocks over 8,000 frames, **0 mismatches**; Linux build 1,214,984 blocks over 2,000 frames, 0 mismatches |
| Toolkit tests | 68000 conformance 59/60 (reference 59/60); SDL virtual-gamepad test passes on Windows (P1/P2, D-pad/stick, A/B/C/D, Start, Back-as-coin) |
| Windows | Release exe built with MSVC 19.51 (VS 18 2026) x64 + SDL2 2.32.10; headless and windowed launches tested |
| Steam Deck | AppImage built and launched under WSL2 Ubuntu 22.04; **not tested on physical Deck hardware** |
| License | PolyForm Noncommercial 1.0.0 (repository license; see `LICENSE-STATUS.md`), confirmed 2026-10-26 |

### The supplied set is the plain, unencrypted MVS release

The `kof97.zip` in `game/` is the exact MAME `kof97` set. CRC-32 of every
file was checked against `ROM_START( kof97 )` in MAME's
`src/mame/snk/neogeo.cpp`:

```
232-p1.p1    1 MB   7DB81AD9   fixed program bank (byte-swapped in the file)
232-p2.sp2   4 MB   158B23F6   banked program image (byte-swapped)
232-s1.s1  128 KB   8514ECF5   fixed layer
232-m1.m1  128 KB   45348747   Z80 sound program
232-c1.c1    8 MB   5F8BF0A1   sprite plane 0/1
232-c2.c2    8 MB   E4D45C81   sprite plane 2/3
232-c3.c3    8 MB   581D6618   sprite plane 0/1
232-c4.c4    8 MB   49BB1E68   sprite plane 2/3
232-c5.c5    4 MB   34FC4E51   sprite plane 0/1
232-c6.c6    4 MB   4FF4D47B   sprite plane 2/3
232-v1.v1    4 MB   22A2B5B5   ADPCM-A samples
232-v2.v2    4 MB   2304E744   ADPCM-A samples
232-v3.v3    4 MB   759EB954   ADPCM-A samples
```

The cartridge has **no encryption, no protection chip and no S ROM banking**.
It uses the standard MVS bank selector at `$2FFFF0`: the low three bits pick a
1 MB window inside the 4 MB banked program image (MAME
`neogeo_base_state::write_banksel`). The `NEO-GEO` signature is present at
`$100` of the fixed bank, and the header's USER / PLAYER_START / DEMO_END /
COIN_SOUND entries are `JMP` stubs at `$122/$128/$12E/$134`.

## Requirements

* **Windows**: Visual Studio 2022/2026 with the C++ workload, CMake 3.21+,
  SDL2 2.x (built against SDL2 2.32.10).
* **Linux**: gcc/g++, CMake 3.21+, make, `libsdl2-dev`.
* Your own legally obtained dumps of the MAME `kof97` and `neogeo` sets.

## Quick start

### 1. Prepare your ROM files

Unzip both sets into one directory, for example `roms-src/`:

```
mkdir roms-src
unzip kof97.zip -d roms-src
unzip neogeo.zip -d roms-src
```

No decryption step is needed. The runtime reads the files directly.

### 2. Build

Windows (from the project root):

```
cmake -S . -B build-windows -G "Visual Studio 18 2026" -A x64 ^
      -DKOF97_ROM_DIR=C:/path/to/roms-src ^
      -DSDL2_DIR=C:/path/to/SDL2-2.32.10/cmake
cmake --build build-windows --config Release --parallel
```

If no SDL2 path is supplied, the build is headless-only. A headless build
needs no SDL2:

```
cmake -S . -B build-headless -G "Visual Studio 18 2026" -A x64 ^
      -DKOF97_ROM_DIR=C:/path/to/roms-src ^
      -DCMAKE_DISABLE_FIND_PACKAGE_SDL2=ON
```

Linux:

```
./scripts/build-linux.sh /path/to/roms-src
# or, by hand:
cmake -S . -B build-linux -DCMAKE_BUILD_TYPE=Release \
      -DKOF97_ROM_DIR=$PWD/roms-src
cmake --build build-linux --parallel "$(nproc)"
```

To build the portable AppImage in one step:

```
./packaging/appimage/build-appimage.sh /path/to/roms-src
```

That writes `dist/steamdeck/kof97-SteamDeck-x86_64.AppImage` (SDL2 is
bundled). Put your `roms/` directory next to the AppImage, or pass
`KOF97_ROM_DIR` / `--rom-path`.

### 3. Run

```
build-windows/Release/"kof 97.exe" --rom-path build-windows/roms
# or
build-linux/kof97 --rom-path build-linux/roms
```

Without `--rom-path`, the player looks for `roms` in the working directory,
`roms` beside the executable, `KOF97_ROM_DIR`, then
`%LOCALAPPDATA%\KOF97\roms` (`~/.local/share/kof97/roms` on Linux). It does
not open a folder picker; if nothing is found the runtime reports the missing
file by name.

Useful flags: `--headless`, `--frames N`, `--input FILE`,
`--screenshot N:FILE`, `--wav FILE`, `--interp`, `--verify`,
`--dump-misses FILE`, `--scale N`, `--fullscreen`, `--mute`. Run `--help`
for the runtime list.

## Controls

| Input | Action |
|---|---|
| Arrows / left stick | move |
| Z X C V / A B X Y (Xbox layout) | Neo Geo A B C D |
| 5 / Back | insert coin |
| 1 / Start | start |
| 2 | player 2 start |
| 3 / left shoulder | select |
| 9 | service credit |
| F2 | test switch |
| F11 | toggle fullscreen |
| Esc | quit |

The pad mapping is the toolkit's fixed SDL GameController layout; a pad SDL
does not recognise can be described with `SDL_GAMECONTROLLERCONFIG`.

On an MVS, insert a coin before Start does anything. The BIOS's coin/start
handling is verified.

## Testing

```
# BIOS -> eye-catcher -> ranking -> intro -> title
"kof 97.exe" --headless --rom-path build-windows/roms --frames 4001 ^
    --screenshot 600:shots/bios.png --screenshot 1200:shots/ranking.png ^
    --screenshot 4000:shots/title.png

# coin -> start -> menus -> match, then walk and attack
"kof 97.exe" --headless --rom-path build-windows/roms --frames 11001 ^
    --input tests/play.txt --screenshot 9600:shots/fight.png

# replay every native block in Musashi and compare
"kof 97.exe" --headless --verify --rom-path build-windows/roms --frames 8001 ^
    --input tests/coin_start.txt

# collect runtime-only entry points, rebuild, and re-measure
cmake --build build-windows --config Release --target profile
cmake --build build-windows --config Release --target kof97
```

Measured results on the Windows Release build (full logs in
`docs/testing.md`):

```
[tests/play_long.txt, 19000 frames, after one profile pass]
[exec] native blocks 14297904, native instructions 354940783,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points

[empty input, 6000 frames, after one profile pass]
[exec] native blocks 3232858, native instructions 113175391,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points

[--verify, tests/coin_start.txt, 8000 frames]
[verify] 6360574 blocks checked, 0 mismatches
```

The recompiler translates **1,342,074 instructions into 41,859 dispatch
entries** from static discovery alone. One profile pass (6,000-frame attract
plus 19,000-frame scripted play) adds 431 runtime-only entry points and brings
both sessions to 0 interpreted instructions; the final table has **42,339
entries** and **1,356,028 instructions**.

### Interpreter comparison

The `--interp` build and the recompiled build produce **byte-identical PNGs**
on static screens (character select and mode select at frames 5000 and 6000
were compared by SHA-256). On screens with per-scanline palette changes (HOW
TO PLAY at 4300, match at 8000) the two modes can differ by a scanline: the
interpreter runs Musashi in cycle-budget slices and can overshoot the
scanline deadline, while recompiled code yields exactly at the event. This is
a host scheduling difference, not a translation error; `--verify` checks every
native block against Musashi with 0 mismatches.

## Audio

The Z80 runs the real M1 driver with NMI/reply latches and ROM banking. The
YM2610's FM, SSG and ADPCM-A/B are synthesized by
[ymfm](https://github.com/aaronsgiles/ymfm), clocked by the Z80, and played
through SDL2 or written with `--wav`. A 3,000-frame coin/start session
produces a 2-channel, 55,555 Hz WAV with peak 11615 and RMS 744, so the path
is alive. The mix has not been listened to critically; treat subjective
quality as unverified.

## Known limitations

* **Steam Deck hardware not tested.** The AppImage was built and launched
  under WSL2 Ubuntu 22.04; physical Deck LCD/OLED, Steam Input and Gaming
  Mode still need validation. If the system lacks FUSE 2, use
  `APPIMAGE_EXTRACT_AND_RUN=1`.
* **Physical gamepads not tested here.** The SDL2 GameController path is the
  toolkit's existing mapping; no physical pad was available in this
  environment.
* **Audio not auditioned.** Signal presence and level are measured; music and
  effect quality are not subjectively verified.
* **One credit / one team session tested.** The scripted session plays a team
  match and reaches the next fighter; later stages, continues and the ending
  are not exhaustively tested.
* **No memory card support** (the toolkit does not implement it).
* **No commercial use.** The project is licensed under PolyForm Noncommercial
  1.0.0; do not assume commercial redistribution is permitted.
* **No ROMs or BIOS included.** You must supply your own legally obtained
  dumps.

## Project layout

```
CMakeLists.txt              build: recompile -> player
src/game.c, game.h          verified ng_game_t: ROM layout
src/main.c                  player (ng_main)
src/rom_select.c/.h         ROM folder discovery
src/recomp_main.c           generator (ng_recomp_main)
tests/coin_start.txt        credit/start script
tests/play.txt              match script (movement and attacks)
tests/play_long.txt         19,000-frame profile script
packaging/appimage/         AppImage build script, desktop file, icon, README
packaging/windows/          Windows package README, ROM helper, SDL2 notice
scripts/build-linux.sh      Linux configure/build helper
scripts/package-windows.ps1 Windows dist packaging
docs/                       compatibility, testing, game and runtime notes
neogeorecomp/               toolkit copy (MIT), with generic fixes
```

## Documentation

* `docs/compatibility.md` - hardware and platform compatibility report.
* `docs/testing.md` - commands and measured results.
* `docs/game-notes.md` - ROM set, banking, boot sequence.
* `docs/runtime-changes.md` - generic changes in the vendored toolkit.

## License

Original code in `src/`, `packaging/`, `scripts/` and the documentation is
licensed under **PolyForm Noncommercial 1.0.0** (see `LICENSE` and
`LICENSE-STATUS.md`), confirmed by the repository owner on 2026-10-26.

`neogeorecomp/` remains MIT (sp00nznet); Musashi and superzazu/z80 are MIT;
ymfm is BSD-3-Clause; SDL2 is zlib. Full attribution is in
`THIRD_PARTY_NOTICES.md` and the preserved `neogeorecomp/LICENSE`, `NOTICE`
and `LICENSES/`.

No SNK ROMs, BIOS images, generated recompiled C or ROM-derived entry lists
are distributed. The King of Fighters '97 and Neo Geo are trademarks of SNK
Corporation. This project is not affiliated with or endorsed by SNK. Supply
your own legally obtained dump.
