"""`data` is a package only so `data.qa` can be materialized beside an adapter.

Before the QA batch this directory had no `__init__.py`, which made it a namespace
package: `import data.alfworld` worked and there was no package object to speak of.
A check that runs inside the verification namespace may not read the platform tree
(`eval/containers/sandbox.py` puts a tmpfs over it), so the check's imports travel with it -- the
scaffold is copied into `<workdir>/data/qa/` and the adapter into `<workdir>/data/`,
and the scaffold's own `from data.qa import base` then has to resolve **there**.

A namespace package cannot be materialized faithfully by copying files: its identity is
the set of directories on the path, and any other `data/` directory would merge with it
rather than shadow it. One empty `__init__.py` makes the package ordinary, so the copy
in the workdir is what `data.qa` means inside the check and `data.<name>` means exactly
the adapter the platform re-materialized.

Nothing else changes: `data/registry.py` discovers datasets by globbing this directory
and imports each as `data.<stem>`, which is what it did before.
"""
