---
title: SQLite WAL loss in HarnessGrad
subtitle: Offline authored controls; no production dataset certified
cols: 3
---
## A The confirmed risk
A SQLite commit can leave new rows in the WAL beside an unchanged main file.
Copying only the main file changed authored BIRD EX from 0 to 1.
The old native bound copy also accepted that altered logical state with a verified digest.

## B What each path preserves
| Path | Finding | Action |
| --- | --- | --- |
| Whole writable-layer image commit | No SQLite filename filter in source | Preserve sidecars; Docker execution remains untested here |
| Selected-file export | Keeps only declared paths | Record dependency-completeness limit |
| Native bound private copy | Used to lose WAL despite verified main digest | Refuse WAL-format SQLite before scoring |
| AppWorld grading | Replays an API log in a fresh world | No AppWorld WAL score change claimed |

## C Evidence and limits
The same focused tests changed from six failures to nine passes.
The refusal writes unmeasured evidence and no reward.
It also refuses closed WAL-mode databases because their headers cannot prove that no WAL was lost earlier.

Generic exports and other sidecars still need complete contracts and trusted source custody.
No blocker closes. The frozen E5 packet retains its inherited source-pin mismatch.

Raw results: reports/w-wal-evidence/

Full analysis: reports/w-wal-receipts.md
