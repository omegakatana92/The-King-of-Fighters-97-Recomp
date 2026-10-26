The King of Fighters '97 - native static recompilation (Windows x64)
====================================================================

This folder contains a native Windows x64 build of The King of Fighters '97.
Its 68000 program was translated ahead of time into C by neogeorecomp and is
executed natively against a model of the Neo Geo MVS board.  The real MVS
system ROM boots the machine; there is no emulator frontend and no BIOS HLE.

It does NOT contain game ROMs or the Neo Geo BIOS.  You must supply your own
legally obtained dumps of the MAME "kof97" and "neogeo" sets.

Quick start
-----------
1. Put the unzipped files of both sets in a folder named "roms" next to
   "kof 97.exe":

     roms\232-p1.p1
     roms\232-p2.sp2
     roms\232-c1.c1 ... 232-c6.c6
     roms\232-s1.s1
     roms\232-m1.m1
     roms\232-v1.v1 ... 232-v3.v3
     roms\sp-s2.sp1   (and the other neogeo BIOS files)

   Prepare-ROMs.ps1 can do this from the two .zip files.

2. Run "kof 97.exe".  If the ROMs are elsewhere, use:

     "kof 97.exe" --rom-path C:\path\to\roms

Requirements
------------
Windows 10/11 x64.  SDL2.dll and the Visual C++ runtime DLLs are included in
this folder.  A Direct3D 11 or OpenGL capable GPU is recommended.

Controls
--------
  Arrows / left stick     move
  Z X C V                 Neo Geo A B C D
  A B X Y (Xbox layout)   Neo Geo A B C D
  5 / Back                insert coin
  1 / Start               start
  2                       player 2 start
  3 / left shoulder       select
  9                       service credit
  F2                      test switch
  F11                     toggle fullscreen
  Esc                     quit

On an MVS you insert a coin before Start does anything.

Command line
------------
  --rom-path DIR        game ROM files (default: roms)
  --bios-path DIR       system ROM files (default: the ROM path)
  --bios FILE           system ROM (default: sp-s2.sp1)
  --headless            no window; run as fast as possible
  --frames N            stop after N frames
  --screenshot N:FILE   save frame N as PNG
  --input FILE          scripted input
  --interp              run everything in the interpreter
  --verify              re-run every recompiled block and compare
  --dump-misses FILE    record interpreted entry points
  --scale N             window scale (default 3)
  --fullscreen          fullscreen, 4:3 pillarboxed
  --wav FILE            write the audio to a WAV file
  --mute                no sound

License
-------
Original project code: PolyForm Noncommercial 1.0.0 (see LICENSES\LICENSE.txt).
neogeorecomp: MIT.  Musashi and z80: MIT.  ymfm: BSD-3-Clause.  SDL2: zlib.
Full attribution is in LICENSES\THIRD_PARTY_NOTICES.txt.  The King of Fighters
and Neo Geo are trademarks of SNK Corporation; this project is not affiliated
with or endorsed by SNK.
