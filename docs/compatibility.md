# Compatibility report

**Game:** The King of Fighters '97 (SNK, 1997), MAME set `kof97` (MVS,
NGM-2320).

**Toolkit:** neogeorecomp v0.2.0 (commit `af96b2b`), vendored with the generic
changes in `runtime-changes.md`.

## Hardware model

| Subsystem | Status | Evidence |
|---|---|---|
| Motorola 68000 | Recompiled C for all code reached; Musashi fallback available | `--verify` 0 mismatches; 100% native on both measured sessions |
| MVS BIOS boot | Works | Real `sp-s2.sp1`: RAM/checksum test, eye-catcher, coins, credits |
| Cartridge header / entry points | Works | BIOS calls USER / PLAYER_START / DEMO_END / COIN_SOUND |
| Program banking | Works | Standard `$2FFFF0` selector, 4 × 1 MB window |
| Encryption / protection | Not present in this set | CRC-verified plain MVS dump |
| Sprite rendering | Works | Attract, menus and match render correctly; 40 MB C ROM |
| Fixed layer | Works | Ranking, menus, HUD text |
| Palettes | Works | Both banks, mid-frame changes |
| Raster effects | Works | Title and stage backgrounds |
| Z80 sound CPU | Works | M1 driver runs, commands/replies latched |
| YM2610 (FM/SSG/ADPCM-A/B) | Produces signal | 3000-frame WAV, peak 11615, RMS 744 |
| SDL2 video | Works | Windowed launch on Windows; AppImage under WSL |
| SDL2 audio | Works | WAV path and live output |
| Keyboard input | Works | Scripted and interactive |
| SDL2 gamepad input | Toolkit mapping, not physically tested | No pad available in this environment |
| Steam Input | Expected to work through SDL2; not validated on a Deck | - |

## Platform status

### Windows x64

* Built with MSVC 19.51 (Visual Studio 18 2026), CMake 4.3.3, SDL2 2.32.10.
* `kof 97.exe` launches headless and windowed; 300-frame windowed run exits 0.
* No decryption step; ROMs are read directly.

### Linux x86_64 / Steam Deck

* Built with gcc 11.4 on Ubuntu 22.04 (WSL2), SDL2 2.0.20.
* AppImage contains the player and `libSDL2-2.0.so.0`; ROMs are not bundled.
* AppRun starts fullscreen, 4:3 pillarboxed, and finds `roms` beside the
  AppImage or `KOF97_ROM_DIR`.
* Verified headless (100.00% native over 6,000 frames), fullscreen (300
  frames under WSLg), with FUSE and with `APPIMAGE_EXTRACT_AND_RUN=1`, and
  with ROM auto-discovery from a `roms` folder beside the AppImage.
* The Linux build's own `--verify` run checked 1,214,984 blocks over 2,000
  frames with 0 mismatches.
* **Physical Steam Deck LCD/OLED and Gaming Mode were not available.** Treat
  Deck hardware compatibility as unverified until tested on a Deck.
* SteamOS normally ships a FUSE 2 runtime, which the AppImage needs. If it is
  missing, `APPIMAGE_EXTRACT_AND_RUN=1 ./kof97-SteamDeck-x86_64.AppImage`
  runs from an extracted directory instead.

## Measured recompilation coverage

| Session | Frames | Native instructions | Interpreted | Coverage | Uncovered entries |
|---|---|---|---|---|---|
| Attract, no input | 6,000 | 113,175,391 | 0 | 100.00% | 0 |
| Scripted play (`tests/play_long.txt`) | 19,000 | 354,940,783 | 0 | 100.00% | 0 |
| Coin/start (`tests/coin_start.txt`), before profiling | 8,000 | 146,232,463 | 3,021 | 100.00% (rounded) | 55 |
| Scripted play, before profiling | 19,000 | 354,447,915 | 494,036 | 99.86% | 386 |

Static discovery alone: 1,342,074 instructions, 27,691 routines, 41,859
dispatch entries. One profile pass adds 431 runtime-only entries; the final
table has 42,339 entries and 1,356,028 instructions, and both measured
sessions run with zero interpreted instructions.

## Correctness

* `--verify`, 8,000 frames with `tests/coin_start.txt`: 6,360,574 blocks
  checked, **0 mismatches**, 0 interpreted instructions.
* 68000 conformance corpus: 59/60 programs pass recompiled, the same as the
  reference interpreter (the remaining program uses a 68020 addressing mode).
* Native vs interpreter screenshots: byte-identical on static screens
  (frames 5000 and 6000). On raster-effect screens the two modes can differ by
  one scanline because of host scheduling; this is documented in the README
  and is not a translation error.

## Known gaps

* Physical Steam Deck and physical gamepads not tested.
* Audio not auditioned subjectively.
* Memory card not implemented.
* AES (`kof97h`), Korean (`kof97k`) and bootleg sets not supported.
* Only one team-match session is scripted; later stages and the ending are
  not exhaustively tested.
