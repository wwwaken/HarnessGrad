#!/usr/bin/env python3
"""Generate an authored v3 VM smoke story; never a benchmark ROM or score control.

The program prints A/newline, waits for an action, and loops. Jericho does not
recognize this ROM identity, so native score/move detection and maximum remain
zero. This exercises load/reset/replay, without positive scoring evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct


def authored_rom() -> bytes:
    rom = bytearray(2048)

    def word(offset: int, value: int) -> None:
        rom[offset:offset + 2] = struct.pack('>H', value)

    rom[0] = 3
    # release, high memory, initial PC, dictionary, object table, globals,
    # static-memory boundary, abbreviations table, declared halfword file size.
    for offset, value in ((2, 1), (4, 0x400), (6, 0x400), (8, 0x90),
                          (10, 0x100), (12, 0x180), (14, 0x400),
                          (24, 0x300), (26, len(rom) // 2)):
        word(offset, value)
    rom[18:24] = b'261015'
    rom[0x40] = 32  # text buffer maximum
    rom[0x70] = 4  # parser-buffer word capacity
    rom[0x91] = 4  # dictionary-entry width; no separators or words
    word(0x145, 0x150)  # object's property-table pointer; empty short name
    word(0x180, 1)  # first global: current room object for v3 status display
    # print_char 'A'; print_char newline; sread text,parse; jump back to print.
    # Jump is relative to the post-operand PC, minus two: signed -11 (fff5).
    code = bytes.fromhex('e57f41 e57f0a e45f4070 8cfff5')
    rom[0x400:0x400 + len(code)] = code
    word(28, sum(rom[64:]) % 65536)
    return bytes(rom)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    payload = authored_rom()
    with args.output.open('xb') as handle:
        handle.write(payload)
    print(json.dumps({'rom': str(args.output), 'sha256': hashlib.sha256(payload).hexdigest(),
                      'bytes': len(payload), 'header_hex': payload[:64].hex(),
                      'code_hex': payload[0x400:0x40d].hex()}, sort_keys=True))
    if args.smoke:
        from jericho import FrotzEnv
        env = FrotzEnv(str(args.output), seed=1)
        try:
            result = {'fully_supported': env.is_fully_supported,
                      'maximum': env.get_max_score(), 'reset': env.reset(),
                      'steps': [env.step('look'), env.step('inventory')]}
            print(json.dumps(result, sort_keys=True))
            assert result['fully_supported'] is False
            assert result['maximum'] == 0
            assert len(result['steps']) == 2
            assert all(step[1] == 0 and step[2] is False and step[3]['score'] == 0
                       and step[0].startswith('A ') for step in result['steps'])
        finally:
            env.close()


if __name__ == '__main__':
    main()
