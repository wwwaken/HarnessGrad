---
title: ujson wheel evidence — task 226
subtitle: Package provenance verified; supported-image runtime closure remains open
template: sheet
theme: paper
cols: 3
lang: en
---

## A What is verified?

The exact ujson 5.10.0 wheel targets CPython 3.12 on glibc Linux x86_64.
The manylinux tag requires glibc 2.17 or newer.

| Evidence | Result |
|---|---|
| Official PyPI JSON URL, size and wheel SHA-256 | ok verified |
| Wheel RECORD and full license bytes | ok verified |
| Fresh local offline installation and file mapping | ok verified |
| Native import and supported image | warn open |

The recorded interpreter is CPython 3.12.4.
The artifact is 53,686 bytes.
Its SHA-256 starts with `f8ccb77b3e40b151`.
The full digest and commands are in `docs/task-226-ujson-wheel-report.md`.

## B What changed the dependency picture?

The published extension differs from the previously installed extension.
Its five direct libraries are:

- `libstdc++.so.6`
- `libm.so.6`
- `libgcc_s.so.1`
- `libpthread.so.0`
- `libc.so.6`

There are no declared Python runtime dependencies.
Static ELF inspection did not execute the loader or import the extension.
The shipped license preserves Electronic Arts, MODP_ASCII and Tcl-derived notices.

## C What still blocks runtime closure?

| Required evidence | Status |
|---|---|
| Approved immutable Python/native image identity | warn missing |
| Actual loader providers and recursive library hashes | warn missing |
| Fresh image-bound offline native import and synthetic round trip | warn missing |
| Bundled double_conversion source/license and required notices | warn review needed |

The wheel defines double_conversion symbols but ships no corresponding notice.
The source revision and applicable terms require authoritative review.
The registry blocker remains external and production authorization remains false.
This task accessed no benchmark dataset, model, endpoint, H0 or pilot.
