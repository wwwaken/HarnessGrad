---
title: Scorer closure audit — Codex 170
subtitle: Source audit and synthetic local controls
template: sheet
theme: paper
cols: 2
lang: en
---

## A Result

Generic scoring still needs production gates for offline dependencies, trusted scorer isolation, artifact export, and official invocation.

The new reusable bundle validator checks declared local bytes. It authorizes no benchmark run.

## B What production enforces

| Gate | Status |
| --- | --- |
| Environment image content address | warn Existing exec control |
| Full offline dependencies | no No generic launch gate |
| Separate scorer image binding | no No bundle binding |
| Artifact-only input export | no Full task tree or snapshot |
| Official scorer invocation | warn Adapter-specific source paths |

Native verifier calls omit network isolation. Exec scoring can inherit task or service networks.

## C Reusable capability

| Function | Purpose |
| --- | --- |
| seal_bundle | Deterministic manifest and SHA-256 |
| load_bundle | Authenticate an external pin |
| verify_bundle | Check exact files and dependency graph |
| require_contract_bundle | Bind separate task contracts |

The receipt states local declared closure integrity. It records declared network policy.

Runtime observations and official provenance remain separate requirements.

## D Evidence and remaining work

84 synthetic tests passed. The tests block subprocess execution and socket creation.

No model, H0, Docker, download, heldout, or dataset execution occurred.

Before diagnostics, each adapter needs a trusted offline runtime, bounded artifact projection, observed isolation, official invocation, and cleanup evidence.

Full details: scorer-closure-codex170-report.md
