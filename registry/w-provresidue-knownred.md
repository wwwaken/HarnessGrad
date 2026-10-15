# Proposed known-red inventory correction — w-provresidue

Replace only the `partially tracked` row at `registry/known-red-tests.md:66` with:

| **partially tracked** (some files committed) | 6 | 166 (historical inventory; B5 replay excluded here) | `external_provenance_b5`: see the measured B5 section below. Other five, 79 unique absences: `e3_bfcl_source` 24 restorable; `hg_wprov` 15 restorable + 2 legitimate empty failure sentinels + 2 recorded 404 + 3 local artifacts without replay URLs; `upstream_provenance_e2` 5 restorable + 9 legitimate empty bodies + 1 unknown (307); `hg_trivia` 13 restorable; `hg_bfcl` 5 restorable. Present pin mismatches: `hg_wprov` 2, `upstream_provenance_e2` 1, `hg_bfcl` 1. Nested `hg_wprov` manifests repeat root paths. Five-packet measurements and dispositions: `registry/w-provresidue.md`. |

The exact text being replaced is:

> These are repository evidence with a real hole. By size: `external_provenance_b5` 87 missing / 147 present / 148 tracked, `e3_bfcl_source` 24/63/64, `hg_wprov` 22/92/1, `upstream_provenance_e2` 15/32/33, `hg_trivia` 13/40/1, `hg_bfcl` 5/16/2.

Evidence: the population table and per-entry citations in `registry/w-provresidue.md`; exact A/K output and input snapshots in `registry/w-provresidue-validation.txt`. The five triples' missing/present counts reproduce; their present counts conceal four wrong digests. “A real hole” is accurate for absent bytes but cannot assert that all five packets have structurally unavailable upstream artifacts: E3, Trivia and BFCL have entirely recorded-200 residue (BFCL separately has a wrong present helper). No other sentence in this file is proved false by this five-packet audit. In particular, “The one with test impact is `external_provenance_b5`” (`:73`) is not contradicted by the static suite-reader search; no five-packet body reader was found.

Do not reinterpret a repeated digest alone as an error page: Trivia's two selected-tree responses reconstruct from retained views to the exact same 973-byte pin. The B5 section's measured error signature is not remeasured or weakened here. No B5 count is freshly asserted, no B5 replay/test was run, and no edit to `known-red-tests.md` is made by this worker.
