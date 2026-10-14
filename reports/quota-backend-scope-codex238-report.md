# Task 238 — quota/backend documentation scope review

Status: documentation clarification complete; no runtime capability or admission
authorization added. Worktree: `/tmp/hg-codex-238`. Reviewed base:
`0930d99cc882c5a049c98f9123e9427470e7e818`.

## Findings and changes

The backend checklist presented provisioning requirements without an explicit
deployment scope. The Terminal packet's “Required quota filesystem” section and
administrator checklist's preference for dedicated empty storage could therefore
read as prerequisites for every user.

- [Installation documentation](README.md) and the
  [backend checklist](docs/filesystem-quota-backends.md) now explicitly permit
  ordinary local execution on existing storage, subject to workload requirements.
  Project quotas and dedicated volumes are not universal prerequisites.
- The strict per-run byte/inode enforcement profile is an optional enhancement
  for formal deployments. Its acceptance requirements remain binding when claiming
  those guarantees. XFS and ext4 are alternatives; a per-run allocation does not
  require a separate physical device or volume.
- Scoped the [Terminal packet](docs/task-211-terminal-operator-backend-packet.md),
  [administrator checklist](docs/task-222-quota-administrator-checklist.md),
  [runner contract](docs/runner-admission-contract.md) and
  [authentication proposal](docs/task-233-quota-readback-authentication.md).
  Updated both existing HTML summaries and the Terminal Markdown source.

Unknown enforcement, cleanup and snapshot evidence stays unknown. Local execution
alone proves no strict-profile guarantee. Capacity, a dedicated volume, supplied
flags, hashes and synthetic checks still do not prove effective enforcement or
trusted observations. Existing gated diagnostic/pilot requirements and runtime
blockers remain intact. Historical reports, source pins and receipts are preserved
at their original review revisions; this task adds no fresh host evidence.

## Validation and limits

- Static checks resolved all 45 relative links in the seven edited Markdown files,
  including the new scope anchors. Backend and administrator checklist item counts
  are unchanged.
- Compared evidence/acceptance sections with the reviewed base: the backend
  evidence contract and appendix, runner API onward, authentication findings onward,
  and Terminal snapshotter section onward are unchanged.
- Regenerated the [Terminal overview](docs/task-211-terminal-operator-backend-overview.html)
  and patched the scope panel in the
  [quota authentication overview](docs/task-233-quota-readback-overview.html)
  with `answer-me-with-html`: six and four panels respectively, zero prose
  warnings. Checked embedded source, local links and absence of remote active
  assets; authentication panels B–D are unchanged.
- Renderer state stayed in this worktree with `AM_HOME` set explicitly,
  `AM_NO_UPDATE_CHECK=1` and `--no-open`; temporary state was removed afterward.
- `git diff --check` passed. Changes are Markdown/HTML only. No runtime tests were
  needed; static checks establish documentation consistency, not backend readiness.

No host inspection or changes, quota/mount operations, dataset/task access,
Docker/container execution, network requests, GPU/model/H0 calls or benchmark runs
were performed. Parent integration and journal updates remain separate.
