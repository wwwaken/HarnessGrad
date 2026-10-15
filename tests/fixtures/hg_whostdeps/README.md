# w-hostdeps evidence packet

Read-only native host inventory for seven explicitly named datasets. No benchmark scoring or production closure is claimed; complete pinned native surfaces remain 0/7.

- `collect.py`, `collect.*`, `host.json`, `imports/`: current host, metadata, source, isolated import-only and static ELF capture. Namespace has loopback only/no routes. Per-command argv/status/stdout/stderr are retained.
- `objects.json`, `sha256sum/`: initial 992 resolved object files, raw readelf/ldd and independent raw hashes. Inspection scopes separate imports, installed supersets and observed tools.
- `supplement.py`, `supplement.*`, `supplement-objects.json`: launcher helpers and version-trace provider supplement; 12 additional unique objects. Original capture outputs are retained.
- `native-dependencies.md`, `facts.json`, `derive.*`: full 1004-object path/digest/provider/scope appendix and derived fractions, not a claim all objects execute during scoring.
- `source/`, `source-index.json`, `source-sites.json`: fresh source preimages/hashes and dependency entry locators. Some upstream source has original whitespace; preserve it.
- `ds1000-context-source.json`, `ds1000-eligible-imports.json`: dependency-only context statements, source hash and eligibility recomputation; no question/reference/test bodies copied. Candidate code is never executed.
- `finalize.*`, `jre-archive*`, `jvm-artifacts.json`, `runtime-resources*`: separate archive/JAR/resource identities, existence observations and independent hash output. Resource inventory is an installed superset, not a sealed runtime.
- `capture-invocations.json`, `cleanup.json`: capture completion and fresh import HOME removal. No run ID or scoring artifact is created.
- `registry-before*`, `validate.py`, `SHA256SUMS`: original registry, raw validation and evidence integrity.

Captured native/Python binaries, packages, fonts, JRE and full payload archives remain at their recorded host paths; this packet retains their hashes and command/source evidence, not copies of the complete runtime. Versions are observations. Source's matching JRE archive digest is a configured artifact pin. Newly recorded digests do not impose an execution pin on mutable host paths.
