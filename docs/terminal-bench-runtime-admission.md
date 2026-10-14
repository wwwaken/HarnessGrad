# Terminal-Bench `cached-runtime-admission` — identity requirements review

Source-only review. No image was pulled, no container was started, no benchmark task was
executed, no model was called. Every claim below cites a file and a line in this checkout.

The blocker this answers (`docs/dataset-blockers.json`, `terminal_bench` →
`cached-runtime-admission`, family `trusted-verifier-runtime`, status `runtime`):

> observed: The journal reports hardened synthetic admission for six cached train images,
> with offline closure, export and quotas still missing.
> next_action: Review manifest/image/resource/cleanup identity requirements and shared
> unresolved backend gates; cached images are not execution evidence.

## 1. What is established, verified against the code rather than restated from the journal

| Identity requirement | Established? | Where it is enforced |
| --- | --- | --- |
| **Image is content-pinned** | Yes | The adapter declares only a *tag* (`data/datasets/terminal_bench.py:195`, `"image": env_meta["docker_image"]`). `eval/containers/container.py:672` resolves it with `resolve_digest(...)` before launch, and `:603` refuses with a message naming the interface contract when it cannot. So a curve point cannot be recorded against an unpinned image. |
| **The resolved digest is recorded** | Yes | `eval/run/runner.py:296` writes `image_digest` into the task's environment record for an `exec` env. |
| **A produced snapshot is content-pinned** | Yes | `eval/containers/container.py:889-894`: the result of `docker commit` is checked with `looks_pinned(image_id)` and a failure is reported as a named kind (`snapshot commit failed kind=docker`), not swallowed. |
| **The admission binding names a manifest** | Yes | `eval/admission/runner_admission.py:62-65`: the binding object must carry exactly `{adapter_id, run_id, trial_id, manifest_sha256}`, and the manifest field must be a SHA-256 (or explicitly null). A binding without one is rejected as `invalid_binding`. |
| **Uncertainty quarantines rather than releases** | Yes | `eval/admission/runner_admission.py:76` and `:91` set `receipt["lease_action"] = "quarantine"`, so an incomplete observation retains capacity instead of freeing it. |
| **Cleanup is admitted, not assumed** | Yes | `eval/admission/runner_admission.py:207` — `admit_cleanup(binding, policy, observed)` is a separate decision from cleanup having happened. |

These corroborate the journal entry the blocker cites (`docs/adapter-integration-journal.md:550-555`,
Codex 112, commit `b3e5409`): admission rejects image-ID mismatches, runtime-envelope
mismatches, negative reservations, unsafe mount flags and ambiguous cleanup absence, and
leases quarantine on uncertainty.

## 2. What is NOT established

1. **No execution evidence exists.** The six cached images are **cached artifacts**. The
   blocker's own next_action says it plainly, and nothing in this review changes it: a
   cached image proves that bytes are on disk, not that a terminal-bench task ran, that its
   verifier scored it, or that the platform can do either repeatably. **No official
   benchmark execution has been performed for this dataset**, and none is claimed here.
2. **The full image set is absent, and obtaining it is not required.** Measured in the
   adapter's own docstring (`data/datasets/terminal_bench.py:318-324`): 89 images, ~104 GB
   total, unevenly distributed (`mteb-retrieve` alone is 21.6 GB). Three tasks
   (`mteb-leaderboard`, `pytorch-model-recovery`, `reshard-c4-data`) **could not be fetched
   on this host at all** — `TLS handshake timeout` partway through a layer. The host
   currently has 122 GB free on `/` with Docker's store on the same filesystem, so the full
   pull would fill it.

   **Operator decision (2026-10-15): a partial run is sufficient.** The platform does not
   need the whole benchmark to establish that this dataset's gates work; it needs enough
   tasks to exercise the verifier and the lifecycle receipts. This is already a first-class
   mode of the adapter rather than something to be built: `data/datasets/terminal_bench.py:118`
   reads `HG_TB_TASKS` and `:260` reports the selection, so a named subset can be run
   without touching production code. The images for such a subset are already cached locally
   — the `jevloop-tb:*` family, at least ten tags, roughly 6 GB in total.
3. **Resource enforcement is not proven, and is no longer required.** Byte/inode quota
   enforcement was the shared blocker `paired-filesystem-quotas`; the operator withdrew that
   requirement on 2026-10-15 (`docs/filesystem-quota-decision.md`). The admission layer's
   own statement still stands — reservations and free-space preflight are not enforcement —
   but enforcement is no longer a precondition, so this is a recorded limit rather than an
   open gate.
4. **Offline closure, trusted runtime and state export remain import gaps** — the shared
   blockers `scorer-offline-closure`, `pristine-verifier` and `artifact-only-state-export`,
   tracked once each rather than repeated per dataset.

## 3. Verdict

**The dataset-specific blocker stays open, with its `observed` sharpened.** The review its
`next_action` asked for has been performed, and its result is not "closed": it is that the
*identity* requirements are genuinely enforced and verifiable in code, while the thing the
blocker actually guards — execution evidence — still does not exist, and three of the
required images cannot be obtained on this host.

Recording this as closed would be exactly the failure the blocker exists to prevent:
counting a cached image, or a review of the rules, as a measurement. What changes is that
the record now says **which** requirements hold and **why** the gate is still shut, instead
of leaving a reader to infer it.

## 4. What would close it

- **one real terminal-bench task run on this host with its verifier producing a score**,
  recorded with the manifest/image/resource/cleanup receipts the admission layer already
  requires. Per the operator decision above this is deliberately a **subset**, selected with
  `HG_TB_TASKS` from the locally cached `jevloop-tb:*` images (~6 GB), not the full 89-image
  set. Nothing about that subset run is claimed here: it has not been performed, and this
  review must not be read as evidence that it would pass; and
- the remaining shared gates closed or explicitly accepted as standing limits —
  `scorer-offline-closure`, `pristine-verifier` and `artifact-only-state-export` are still
  open reviews, and `runtime-observations` still asks for its observation source to be
  integrated against the existing refusal contract. The quota gate is no longer among them.

The subset run is the part this review could not do — it needs the GPU endpoint and a real
execution, which is a separate, budgeted step, not a source review. It is not blocked on
anything the operator has to decide.
