---
title: Task 198 — LiveCodeBench row provenance
subtitle: Public metadata research · 14 October 2026
template: sheet
theme: paper
lang: en
cols: 2
---

## A Gate remains blocked

The search found no qualifying independent attestation for local row 740 → `abc360_a`.
The search could not inspect the pinned Hugging Face metadata or official loader contents.
These failures leave the dataset-side search unresolved.

## B What the evidence establishes

| Evidence | Result | Limit |
| --- | --- | --- |
| Official pinned GitHub tree | Complete path inventory | Locates the loader; does not show its behavior |
| Source commit signature | GitHub reports verified | Does not attest to a dataset row |
| GitHub Releases and Tags | Empty API lists | Does not exclude dataset-side configurations |
| Hugging Face metadata | Requests failed | Cannot establish absence of an attestation |

## C Which row needs custody

Local code unions six shards and sorts their question IDs.
The adapter assigns zero-based indices after the header.
Local index 740 therefore differs from an unspecified upstream ordinal.
Its `train` claim belongs to the HarnessGrad split.

The release pin, source signature, pool hash and statement hash do not independently establish this mapping.

## D What to request

Ask the upstream maintainers for release metadata and any authenticated row-index evidence.
Ask the independent pool custodian to substantiate the sorted rank, pool custody and local split.
Require a detached custody envelope and a separately approved exact-byte record digest.
Keep the gate blocked when any claim lacks evidence.

This work produced an unsent custodian request.
No pool rows, prompts, tests, solutions or heldout payloads were read.
No H0, model or main-branch work occurred.

Full details: [research report](task-198-livecodebench-provenance-report.md) and [custodian request](task-198-livecodebench-custodian-request.md).
