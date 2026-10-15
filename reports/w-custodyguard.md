# w-custodyguard: preserve custody without forbidding own-group export access

Resolution **A**: forbid elevation, allow identity reads, and forward ownership calls only with `uid=-1` and `gid=os.getegid()`. The module documents this choice and cites the root export call (tests/quality/test_optional_backend_api_codex241.py:3; eval/admission/artifact_admission.py:351). Production exports deliberately grant the scorer group read/search access while retaining platform custody (eval/admission/artifact_admission.py:334).

**FOUND — local non-root control:** observed `uid=1026 euid=1026 gid=1026 egid=1026`; `os.chown(path, -1, os.getegid())` succeeded, preserved the owner, and left the group equal to the effective group. This verifies the allowed operation locally; it does not establish sandbox scorer readability (reports/w-custodyguard-validation.txt:638; see that record's exact command).

**FOUND — enforced guard:** all ten existing setter/shell prohibitions remain and are exercised; four identity reads remain available. Each of `chown/fchown/lchown` rejects an owner change or foreign group before calling the saved real OS operation, and records successful allowed calls. Positive controls check the real file owner/group and recorder; negative controls check refusal, empty recorder and unchanged metadata. The existing integration case checks that export root and file calls passed through the recorder (tests/quality/test_optional_backend_api_codex241.py:27, :34, :49, :64, :82, :93, :98).

**FOUND — tests and negative execution:**

- Before: `6 errors in 0.10s` (reports/w-custodyguard-validation.txt:615).
- After: `29 passed in 0.11s`, including the original six cases and new guard controls (reports/w-custodyguard-validation.txt:906).
- Related scorer admission/backend modules: `75 passed in 0.25s` (reports/w-custodyguard-validation.txt:927).
- A temporary positive-control mutation passed `os.getegid() + 1` to `chown`; observed `1 failed in 0.06s`, pytest exit 1, and byte-identical restoration (reports/w-custodyguard-validation.txt:996). The exact command and complete failure are in validation record 10. The restored module passed again in validation record 13.

Observed failure excerpt, verbatim (reports/w-custodyguard-validation.txt:987):

```text
>       assert gid == os.getegid(), "offline API attempted foreign-group chown"
E       AssertionError: offline API attempted foreign-group chown
E       assert 1027 == 1026
```

**FOUND / ABSENT — duplicate guard search:** before editing, `git grep -n 'offline API attempted identity' -- .` searched all git-tracked paths in the assigned worktree and returned only this module's old refusal at line 19 (validation record 3). Thus an additional module matching that exact text was ABSENT in that enumerated Git scope. After editing, the exact-message search under all git-tracked `eval/` and `tests/` paths returned exit 1 with empty stdout/stderr (reports/w-custodyguard-validation.txt:1020). Semantically similar guards with different messages are UNKNOWN.

**FOUND — every final `git grep -n 'chown' -- eval/ tests/` hit:** exact output is in validation record 12. “Unreachable as a call” below classifies text, predicates, parameter declarations, handle selection and expected records; it does not assert that their surrounding code is unreachable.

| Hit | Disposition |
| --- | --- |
| eval/admission/artifact_admission.py:351 | Legitimate group set on the export root: owner untouched, own effective group. |
| eval/admission/artifact_admission.py:367 | Legitimate group set on a newly created selected-path parent, with the same arguments. |
| eval/admission/artifact_admission.py:371 | Legitimate group set on an exported file, with the same arguments. |
| tests/fixtures/hg_migration_site/adapter-integration-journal.md:2912 | Unreachable as a call: retained explanatory prose about the group assignment. |
| tests/quality/test_optional_backend_api_codex241.py:36 | Unreachable as a call: assertion rejecting owner changes. |
| tests/quality/test_optional_backend_api_codex241.py:37 | Unreachable as a call: assertion rejecting foreign groups. |
| tests/quality/test_optional_backend_api_codex241.py:43 | Unreachable as a call: names used to install checked wrappers. |
| tests/quality/test_optional_backend_api_codex241.py:49 | Legitimate group-set control parameter list; actual forwarded call is at :57. |
| tests/quality/test_optional_backend_api_codex241.py:56 | Unreachable as a call: select a descriptor for fchown, otherwise a path. |
| tests/quality/test_optional_backend_api_codex241.py:64 | Owner-change / foreign-group negative control parameter list; attempts at :76 are refused. |
| tests/quality/test_optional_backend_api_codex241.py:74 | Unreachable as a call: select the negative control's descriptor/path. |
| tests/quality/test_optional_backend_api_codex241.py:102 | Legitimate group-set expected record for the export root; no syscall here. |
| tests/quality/test_optional_backend_api_codex241.py:103 | Legitimate group-set expected record for the export file; no syscall here. |

**FOUND — registry check:** `python3 tools/check_dataset_blockers.py` returned exactly:

```json
{"valid": true, "datasets": 28, "shared_blockers": 0, "historical_records": 11, "production_authorized": false}
```

Evidence: reports/w-custodyguard-validation.txt:887. This change does not edit the registry: before deliverables, the sole changed tracked file was the target test (reports/w-custodyguard-validation.txt:1257). No registry proposal is warranted for a test guard repair.

**FOUND — cleanup:** the sequential final check observed `Remaining custodyguard /tmp directories: []` (reports/w-custodyguard-validation.txt:1243). An earlier cleanup assertion accidentally ran alongside the restored pytest run and observed its active temporary directory; its exact failed output is retained in validation record 11, rather than treated as successful cleanup.

**UNKNOWN — main review uncertainty:** an actual sandbox/container scorer UID reading these exports was not exercised. Resolution B was not chosen; production code and existing scorer assertions remain untouched in the observed diff (reports/w-custodyguard-validation.txt:1257). Full-suite coverage, non-Linux behavior and privilege paths outside these guarded OS APIs are also unverified (validation's NOT VERIFIED list).
