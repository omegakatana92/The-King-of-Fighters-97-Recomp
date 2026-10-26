# The King of Fighters '97 - game and hardware notes

## ROM set

MAME set `kof97` (MVS, NGM-2320). All CRCs verified against
`ROM_START( kof97 )` in MAME's `src/mame/snk/neogeo.cpp`:

| File | Size | CRC-32 | Role |
|---|---|---|---|
| `232-p1.p1` | 1 MB | `7DB81AD9` | fixed program bank |
| `232-p2.sp2` | 4 MB | `158B23F6` | banked program image |
| `232-s1.s1` | 128 KB | `8514ECF5` | fixed layer |
| `232-m1.m1` | 128 KB | `45348747` | Z80 sound program |
| `232-c1.c1` | 8 MB | `5F8BF0A1` | sprite planes 0/1 |
| `232-c2.c2` | 8 MB | `E4D45C81` | sprite planes 2/3 |
| `232-c3.c3` | 8 MB | `581D6618` | sprite planes 0/1 |
| `232-c4.c4` | 8 MB | `49BB1E68` | sprite planes 2/3 |
| `232-c5.c5` | 4 MB | `34FC4E51` | sprite planes 0/1 |
| `232-c6.c6` | 4 MB | `4FF4D47B` | sprite planes 2/3 |
| `232-v1.v1` | 4 MB | `22A2B5B5` | ADPCM-A |
| `232-v2.v2` | 4 MB | `2304E744` | ADPCM-A |
| `232-v3.v3` | 4 MB | `759EB954` | ADPCM-A |

System ROMs (from the `neogeo` set): `sp-s2.sp1` (default MVS BIOS),
`sfix.sfix`, `sm1.sm1`, `000-lo.lo`.

The AES release (`kof97h`, `232-pg1.p1` CRC `5C2400B7`) and the Korean
release (`kof97k`, `232-m1k.m1`) are different sets and are not used here.
The bootleg `kof97pls` / `kof97oro` sets are not supported.

## Program layout and banking

```
$000000-$0FFFFF   fixed bank     232-p1.p1
$200000-$2FFFFF   banked window  232-p2.sp2, selected by $2FFFF0
$C00000-$C1FFFF   system ROM
```

The cart uses the standard MVS scheme: a write to `$2FFFF0` selects one of
four 1 MB banks through the low three bits of the value (MAME
`neogeo_base_state::write_banksel`: `bank = data & 7`,
`m_bank_base = (bank + 1) * 0x100000`). The runtime's
`ng_bank_base` is the offset inside the 4 MB banked image, so selector 0 maps
to `prom + 0x100000`, the same as hardware.

There is no NEO-SMA / NEO-CMC encryption, no protection read and no S ROM
banking. `src/game.c` therefore uses only the generic fields of `ng_game_t`.

### Header

`$100` contains `NEO-GEO`, and the four BIOS entry points are `JMP` stubs:

```
$122  USER          JMP $009868
$128  PLAYER_START  JMP $00956E
$12E  DEMO_END      JMP $009B6A
$134  COIN_SOUND    JMP $009BEC
```

The reset vectors point at the BIOS (`$00C00402`), as on a real MVS.

## Boot sequence observed

| Frame | Screen |
|---|---|
| ~600 | `NEO-GEO` BIOS eye-catcher |
| ~1200 | CHARACTERS RANKING |
| ~2400 | intro artwork |
| ~4000 | title screen |
| ~4300 | HOW TO PLAY (after coin + start) |
| ~5000 | CHARACTER SELECT |
| ~6000 | MODE SELECT (ADVANCED / EXTRA) |
| ~7000 | ORDER SELECT |
| ~8500 | match, ROUND 1 |
| ~9900 | K.O. / PERFECT, next team member |

Frame numbers vary with the input script; the ones above are from
`tests/coin_start.txt` and `tests/play_long.txt`.

## Hardware features exercised

* **68000** at 12 MHz, all instructions; recompiled C.
* **MVS BIOS** boot, checksum, RAM test, coin/credit handling, calendar.
* **LSPC** sprite rendering with per-scanline evaluation, sticky chains,
  shrink tables from `000-lo.lo`, 96-sprites-per-line limit, auto-animation.
* **Fixed layer** 128 KB S ROM, both palette banks.
* **Raster timer IRQ** for mid-frame palette changes.
* **Z80** sound CPU with NMI command/reply latches and banked M1 access.
* **YM2610** FM, SSG and ADPCM-A/B through ymfm.
* **Watchdog**: the game kicks `$300001`; the runtime resets the board if a
  kick does not arrive within 1,622,015 68000 clocks, as MAME does.
* **uPD4990A** calendar, seeded from the host clock.

## Not implemented / not exercised

* Memory card.
* AES mode (`kof97h`).
* Link-up / versus cabinet.
* Later stages and the ending were not exhaustively tested.
