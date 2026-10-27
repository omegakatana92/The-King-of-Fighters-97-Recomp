The King of Fighters '97 - native static recompilation
======================================================

This AppImage contains the recompiled game and the SDL2 window/audio layer.
This build (v0.1.1) fixes the M1 bank-mask bug that silenced the
character-select background music.  It does not contain game ROMs or the Neo
Geo BIOS: supply your own legally obtained dump.

Quick start
-----------
1. Put your MAME "kof97" set and "neogeo" set in a folder, unzipped:

     mkdir -p roms
     unzip kof97.zip -d roms
     unzip neogeo.zip -d roms

   The AppRun script finds a "roms" directory next to the AppImage, a folder
   named by KOF97_ROM_DIR, or the per-user folder
   $HOME/.local/share/kof97/roms.

2. Make the AppImage executable and run it:

     chmod +x kof97-SteamDeck-x86_64.AppImage
     ./kof97-SteamDeck-x86_64.AppImage

   It starts in fullscreen with a 4:3 pillarboxed image.

If no ROM folder is found the game reports the missing file by name.  In
Gaming Mode, put the roms folder next to the AppImage or set KOF97_ROM_DIR
in the game's launch options.

If the system has no FUSE 2 runtime (some minimal SteamOS images), run the
AppImage in extraction mode instead:

     APPIMAGE_EXTRACT_AND_RUN=1 ./kof97-SteamDeck-x86_64.AppImage

Steam Deck
----------
Copy the AppImage and a roms folder to the Deck, mark the AppImage executable,
and add it as a non-Steam game.  It runs in Game Mode and Desktop Mode.

Controls
--------
  D-pad / left stick     move
  A B X Y (Xbox layout)  Neo Geo A B C D
  Back                   insert coin
  Start                  start
  Left shoulder          select
  F11                    toggle fullscreen
  Esc                    quit

Steam Input: the AppImage uses SDL2's GameController API.  The default Steam
Deck template maps the built-in controls to a standard pad, so no extra
configuration is needed.  If you use a custom layout, keep A/B/X/Y, the
D-pad or left stick, Start and Back mapped.

The game boots the real MVS BIOS, so insert a coin (Back) before Start.

License
-------
The original project code is PolyForm Noncommercial 1.0.0.  The bundled
neogeorecomp runtime is MIT; Musashi and z80 are MIT; ymfm is BSD-3-Clause;
SDL2 is zlib.  Full notices are in usr/share/doc/kof97/.  No ROMs or BIOS
images are included.  The King of Fighters and Neo Geo are trademarks of SNK
Corporation; this project is not affiliated with or endorsed by SNK.
