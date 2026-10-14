# Data namespace split verification

Worktree: `/tmp/hg-ds`, starting at `fdef36a`. All implementation and review
happened here; no integration merge or frozen-receipt execution was performed.
Stage B (`ad25c7d`, `5cb804e`) was already present and is not repeated.

## Stage A

Moved `data/qa/`, `registry.py`, `command_control.py`, and
`command_oracle_harness/` into `data/scaffolds/`. Added documented temporary
module aliases at the old Python paths, including submodules and direct script
entry points. Standalone QA CLI/prediction assets use temporary links, since
existing callers copy their bytes. Adjusted root/discovery paths for the extra
level. No adapter changed. Import-direction exceptions follow the moved files;
the same test file now guards scaffold declarations and private asset directories.
`pinchbench` is explicitly unclassified rather than assumed to be an adapter.

Command (guard included in `test_import_direction.py`):

```sh
python3 -m pytest -q -p no:cacheprovider --basetemp=/mnt/20t/xubuqiang/.hg-pytest/ds/a tests/quality/test_import_direction.py tests/quality/test_dataset_lint.py tests/quality/test_dataset_blockers.py tests/quality/test_new_dataset.py
```

Exact final output:

```text
........................................................................ [ 78%]
....................                                                     [100%]
92 passed in 42.22s
```

Additional compatibility inspection: old and canonical registry/base modules
have the same identity; publication still returns 28 names; the relocated
command oracle harness exists. `git diff --check` passes.

The first attempt exposed a wrapper root-depth error (fixed) and a missing
pytest basetemp parent (created). A successful intermediate run reported
`92 passed in 51.73s`; the final run above includes the optimized guard.
