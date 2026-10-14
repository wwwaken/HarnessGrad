# Supplemental notices for the existing task-226 wheel

Retain **both complete files** with the eventual binary distribution and its
documentation/materials. No binary was repacked or installed in B6.

- `ujson-LICENSE.txt` is an unchanged copy of the exact wheel's combined license
  already preserved by task 226; it also matches the acquired 5.10.0 source blob.
- `double-conversion-LICENSE` is the unchanged decoded original upstream blob
  `933718a9ef9dae4cb4afa56e490211760d8a949f`, at ujson commit
  `59875e089937c8b05c2f4b474530e3a9ec706a56`, path
  `deps/double-conversion/LICENSE` (identical to COPYING in that tree).

The parent review records the precise vendored tree, source/default-build evidence,
and the wheel's existing double_conversion ELF-symbol observation. These notices
do not authenticate a wheel build's source, establish all third-party rights, or
close supported-image/native runtime requirements. The deployment owner must carry
these files into the actual deployment bundle and obtain the missing receipts.
