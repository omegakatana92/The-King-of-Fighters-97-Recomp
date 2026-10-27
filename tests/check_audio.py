#!/usr/bin/env python3
"""Regression check for the KOF '97 audio fix.

Run the player with tests/play_long.txt (coin at frame 900, start at 1000,
character select around frame 5000, match around frame 8500), write a WAV,
then check that the music is continuous from character selection through the
match instead of going silent with only isolated samples.

Usage: tests/check_audio.py <capture.wav>

Before the M1 bank-mask fix the 83-120 s window (character select, mode
select and order select) was almost entirely silent. After the fix every
1 s window in 83-202 s is above 100 RMS.
"""
import math
import struct
import sys
import wave

MIN_RMS = 100.0
MIN_PEAK = 1000
WINDOWS = ((83, 120), (120, 170), (170, 200))


def fail(msg):
    print(f"FAIL: {msg}")
    return 1


def main(path):
    try:
        w = wave.open(path, "rb")
    except OSError as e:
        return fail(f"cannot open {path}: {e}")
    rate, channels, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
    n = w.getnframes()
    raw = w.readframes(n)
    w.close()
    if rate < 8000 or channels not in (1, 2) or width != 2:
        return fail(f"unexpected WAV format: {rate} Hz, {channels} ch, {width * 8} bit")

    samples = struct.unpack("<%dh" % (len(raw) // 2), raw)
    if channels == 2:
        mono = [(samples[i] + samples[i + 1]) / 2.0 for i in range(0, len(samples), 2)]
    else:
        mono = list(samples)

    peak = max((abs(x) for x in mono), default=0)
    if peak < MIN_PEAK:
        return fail(f"capture is silent (peak {peak:.0f})")

    secs = []
    for start in range(0, len(mono) - rate + 1, rate):
        block = mono[start:start + rate]
        secs.append((start // rate, math.sqrt(sum(x * x for x in block) / len(block))))

    for a, b in WINDOWS:
        seg = [r for t, r in secs if a <= t < b]
        if not seg:
            return fail(f"capture is shorter than {b} s")
        quiet = [t for t, r in secs if a <= t < b and r < 50.0]
        minimum = min(seg)
        if quiet:
            return fail(f"{a}-{b} s has silent windows at {quiet[:12]}")
        if minimum < MIN_RMS:
            return fail(f"{a}-{b} s minimum RMS {minimum:.0f} is below {MIN_RMS}")
        print(f"{a:3d}-{b:3d} s: min RMS {minimum:7.1f}  mean RMS {sum(seg) / len(seg):7.1f}")

    print(f"PASS: continuous audio through character select and the match (peak {peak:.0f})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: tests/check_audio.py <capture.wav>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
