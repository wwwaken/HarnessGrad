# AgentDojo metadata-only provenance reconciliation — Codex 190

Production remains **blocked** under `production-route-admission`. The inherited
directory-presence inventory agrees with the adapter's declared layout, but it
does not authenticate a release, selected groups, prepared rows, installed
dependencies, or runtime contents. No production readiness follows from this
audit. No adapter, registry, H0, model, or main changes were made.

## Evidence boundary

Worktree: `/tmp/hg-codex-190`, detached base commit
`a58b4b181193a2e2b201c6353722725ad77b597c`; base tree
`4efc675ea0af224fe8cc97d8e5c9999ef741ab0e` (Git SHA-1 objects).
The worktree was initially clean. The accompanying
`agentdojo-provenance-codex190-metadata.json` records scoped identities and their
canonicalization. It is a newly computed **local metadata record**, not an
authenticated upstream release or custodian manifest.

Inspected only checkout source declarations, repository documentation, blocker
metadata, filenames, and Git commit/tree/index metadata. Source was parsed
statically; the adapter was never imported. The declared external dataset root
and evidence archives were not inspected, even for fresh filesystem metadata.
Cases, prompts, prepared case/state/gold/action payloads, runtime binaries,
heldout content, and external receipt contents were not opened or hashed.
No network, preparation, provisioning check, verifier, scorer, runtime, model,
H0, or production route was invoked.

The registry's statement that `_src`, `runtime`, `agent_runtime`, and `prepared`
are present is an **inherited external metadata claim**. Its checkout reference
has no per-file inventory, observation timestamp, authenticated inventory
digest, or release binding. It cannot be upgraded into a fresh observation.

## Pins and available release declarations

| Identity axis | Exact local declaration | What this establishes |
| --- | --- | --- |
| Upstream source | `089ed468cf3ed0322acc66b0211f26d9d90dbf60` | Adapter commit pin and codeload URL agree with `DOWNLOADS.md`. Upstream object authenticity was not checked. |
| Source archive | `_src/agentdojo.tar.gz`; expected SHA-256 `d7e0ee021be27a69e7e66647979b5a5e0dd10030d38d04ce4102e18a76a228d8` | Exact expected digest exists in both adapter and generated download documentation. Actual archive bytes were not measured. |
| Package | `agentdojo==0.1.35` | Exact direct version requirement; no wheel/sdist hash or complete installed dependency lock is available in this checkout. |
| Suite | `v1.2.2` | Adapter suite label; no authenticated upstream tag-to-commit or suite-membership manifest is available here. |
| Adapter pool | `TASK_COUNT = 949`; keys `agentdojo/0` through `agentdojo/948` | Declared positional domain, not verified release row membership. |
| Dependency record | `_src/runtime-requirements.lock` | Mentioned by download documentation; contents, digest, and actual installation correspondence are unavailable here. |

`DOWNLOADS.md` identifies itself as generated from the adapter's `downloads()`.
Its agreement is internal consistency, not independent release authentication.
The source commit, package version, and suite version are three axes; equality
or release equivalence cannot be inferred from their labels. The adapter
docstring's shorthand “package/source 0.1.35” does not replace the commit pin.

Tracked-path inventory and a filename-only search including hidden/ignored
checkout paths found no separate AgentDojo exact-release, selected-group,
prepared-row, or installed-runtime manifest. This is a statement about the
available checkout, not about manifests that may exist at the unopened external
dataset root. No upstream fetch or external-manifest inspection was attempted.

## Reconciliation of the inherited path inventory

All external paths below are relative to the **declared** dataset root. Table
entries are source declarations, not fresh file-presence observations.

| Inherited inventory name | Adapter/documentation paths and role | Remaining identity gap |
| --- | --- | --- |
| `_src` | `_src/agentdojo.tar.gz`, `_src/cases.json`, documented `_src/runtime-requirements.lock` | Actual archive digest; extraction/release identity; catalog ordering and row/group membership; installed dependency provenance. |
| `agent_runtime` | `agent_runtime` → setup `dojo_runtime`; `agent_runtime/bin/python` is a presence sentinel | Installed tree/binary/dependency identity and attestation of the declared tool-only contents. |
| `runtime` | `runtime` → verifier input `trusted_runtime`; `runtime/bin/python` is a presence sentinel | Trusted runtime identity, dependency closure, and independent verification evidence. |
| `prepared` | `prepared/{index}/initial.json` → setup state; `case.json` → selected control/verifier input; `oracle.json` → reference action | Binding of each selected positional ID to its release row/group and protected prepared artifacts. |
| Local Git sources | `data/agentdojo/cli/dojo`, `verify/check.py`, `bridge.py` are declared setup/verifier sources | Git source identities are available; materialized/runtime equivalence is not established. |

The four inherited directory names have no contradiction with the declared
layout. They also cannot establish all 949 rows, any selected complete group,
or separation of public setup state from private verifier/reference content.
The source `provision_status()` checks only four sentinels, including
`prepared/948/initial.json`; even a true result would not prove those facts.
That function was not called.

## Hashes safe to compute now

The JSON companion contains the complete scoped Git object list. Object IDs for
preparation, CLI, control, bridge, and verifier source were obtained from Git
tree metadata without opening those files. The explicit source list also
includes `data/__init__.py`, `data/qa/__init__.py`, and `data/qa/base.py`; it is
not a complete transitive import, dependency, harness, or runtime lock.

| Computed identity | Value |
| --- | --- |
| `data/agentdojo` Git subtree object | `11d857328859f708e1571459db84fdf4f612e3b1` |
| Reviewed adapter source byte SHA-256 | `0cc0b62386178ce8f4cb0589289d7a3001de60d1b217dfb8f3129951363a77b5` |
| Scoped Git source metadata SHA-256 | `22e41ba774105c46b26a5bba95db7c4a4bf89406937a65a0947bb0e02842583d` |
| Declared pin metadata SHA-256 | `2044b245b59942d557f0b90eedae301b28661a26f442236be80d9a4344fc074a` |
| Logical path-template inventory SHA-256 | `47c50c900af09b6d2f0745ce47687b7fe2150c3159757a80aec4ea42625938b1` |

The last three digests cover explicitly named JSON values using UTF-8, sorted
keys, comma/colon separators, ASCII escapes, and no trailing newline. They
authenticate only reproducibility of these local values relative to a trusted
copy. A Git SHA-1 object ID is a typed Git object identity, not a file SHA-256.
Hashing a list of Git IDs does not independently produce SHA-256 digests of the
underlying files. Neither hashes nor path names establish custody.

The companion also records local byte SHA-256 values for `DOWNLOADS.md` and
`docs/dataset-blockers.json`. Those values identify declarations and the
inherited inventory claim, not downloaded artifacts or external receipts.

The declared split **algorithm's source identity** is safely available:
`data/qa/base.py` is Git blob `1cb0b5e5866b2b171414c93d5aa594f699427d83`.
The adapter assigns groups using the suite/user key and the shared deterministic
hash rule. Actual split membership and a split-manifest digest cannot be
computed without an authenticated metadata-only row/group map. The journal's
97 groups, 615 train / 334 eval rows, four selected groups, 35 selected pairs,
and 70 historical control arms remain inherited claims here. None were
recounted or authenticated.

`OFFICIAL_EVAL = None` declares the whole adapter pool as official evaluation;
the adapter's train/eval group partition is a separate axis. A custodian record
must name which axis it binds. Taxonomy also remains separate: demand
`tool_use`, surface `tool_dialogue`, exercises `context/tools/control/safety`.

## What requires custody or other independent evidence

| Missing identity/evidence | Why Git/source metadata cannot supply it |
| --- | --- |
| Actual archive and extracted release | Expected download SHA-256 is available, but actual bytes and trusted commit/archive/package/suite correspondence are not. |
| Catalog, prepared artifacts, row ordering and group alignment | Numeric adapter keys are positional; source code cannot attest the protected data used at preparation time or their current bytes. |
| Declared/official split and selected complete-group manifest | Source identifies the rule, not the release-specific inputs, membership, selection, counts, or custody. |
| Installed dependency lock and both runtime identities | A version string and generator Git identity do not describe installed packages, binary bytes, runtime trees, or their separation. |
| Full model/harness identity for a production receipt | No model or harness was selected; repository HEAD is not an installed model digest or a complete harness/runtime closure. |
| Fresh verifier, isolation, quota, snapshot/export and cleanup evidence | Source identities describe intended code, not observed backend enforcement, trusted execution or lifecycle outcomes. Historical receipt paths were not opened. |

A custodian can supply a bounded metadata-only record with provenance,
canonical adapter IDs, release-row/group binding, declared/official side,
selected membership and coverage, protected artifact digests, dependency/runtime
identities, and an independently trusted attestation/digest. This reviewer can
then compare that record to the pins without reading protected bytes. A
self-generated hash with no trusted custodian or release binding is insufficient.
Digests of protected content should be accepted only through that approved
metadata channel; this audit does not hash protected bytes itself.

## Exact remaining production gate

`production-route-admission` remains `runtime` and production authorization
remains false. Missing evidence has two distinct parts:

1. **Provenance/custody:** an independently authenticated metadata-only release
   and selected complete-group record binds the declared source commit/archive
   digest, suite and package axes, positional IDs, group/split membership,
   preparation source, protected selected artifact digests, dependency lock,
   and both installed runtime identities. No inferred 949-row alignment or
   historical split/control count can substitute for this record.
2. **Admission/lifecycle:** independent review of a selected-only, non-scoring
   admission contract and fresh evidence tying its coherent source lock and
   approved artifact identities to the actual production route. Existing gaps
   include trusted verifier/runtime and dependency/offline closure, selected-only
   materialization/privacy, artifact-only export, observed filesystem/resource
   limits and network boundaries, bounded snapshot lifecycle, and owned cleanup.
   These observations must share an immutable identity-bound receipt; source
   inspection and synthetic metadata guards are insufficient.

Any measurement receipt would additionally need the stated metric identity
(utility and separately recorded attacker-success semantics), eligible/selected
task and trial coverage, invalid/unmeasured counts, source/split/manifest/model/
harness identities, endpoint binding, resource/budget limits, cleanup receipt,
and comparability notes. None is supplied by a directory inventory. This report
contains no measured diagnostic receipt and authorizes no diagnostic or pilot.

No such custody record or fresh production admission/lifecycle receipt is
available in this audit. The Codex 180 metadata privacy closure stays closed;
this report neither reopens it nor extends it into runtime authorization.
Historical controls and journal summaries remain unverified evidence references.
This gate statement is an evidence inventory, not an execution or scoring plan.

## Validation

Static reconciliation checked adapter/download commit, suite, package, and
expected archive digest agreement; the active registry blocker was asserted
unchanged. Scoped Git identities, canonical JSON digests, and safe local source
hashes were recomputed against the companion record. Report/JSON/journal changes
were reviewed and `git diff --check` passed. No runtime tests were needed for
these documentation-only outputs; inherited test counts were not reported as
new validation. All generated files stayed in this isolated worktree.
