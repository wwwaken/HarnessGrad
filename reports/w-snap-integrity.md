# Actor snapshot integrity — w-snap

The normal actor-to-verifier path carries the actor's **committed image identity**, under a trusted local Docker daemon and trusted host caller. It is **not bound to an unchanged committed filesystem at check time**: an actor-controlled startup executable changed a committed file when the verifier started. Independent w-snap2 checks confirm this through the actual verifier function. They also show that a different existing digest supplied directly to that function is **not refused**: there is no separate expected-identity comparison. A separate inherited-volume control lost actor output. No scoring logic was changed and no benchmark scorer ran.

Snapshot image binding established; unchanged verification filesystem refuted by actor-controlled startup.

## Creation, identification and consumption

Source references below refer to the original sources pinned in `tests/fixtures/hg_wsnap/source-pins.json`, at starting commit `48c2848` (full hash in `raw/001.stdout.txt`). At the w-snap2 baseline, container.py/container_state.py remain byte-identical; verifier.py changed only in its separate `_verify` dispatch below the snapshot path. `independent/current-source-pins.json` pins current bytes without replacing the original pins, and `independent/packet-audit.json` records the independently checked route equivalence.

- `eval/containers/container_state.py:51-53,92-109` creates an actor name and snapshot tag, then creates the actor from `env_spec["image"]`. Harness/runtime binds are read-only; scratch/home use tmpfs. The task filesystem is not a shared workdir bind.
- `eval/containers/container_state.py:184-200` stops the entire actor before committing; snapshot failures become invalid results. `eval/containers/container.py:860-872` runs `docker stop --time 5`; `:875-894` admits size/headroom, runs `docker commit <actor> <tag>`, validates the returned string's **syntax** with `looks_pinned` (`:293-303`), and returns that string, **not the tag**. This syntax check neither authenticates its origin nor compares it with a separately expected identity.
- `eval/containers/container_state.py:213-219` passes the returned `snapshot` directly to `_verify_container_state`; `eval/verification/verifier.py:248-252,290-292` passes that value to `container.create(image=snapshot)`; `eval/containers/container.py:786-794` puts it verbatim in `docker create ... <image> sleep infinity`. No tag re-resolution occurs in this path.
- `eval/verification/verifier.py:274-284,301-321` adds the platform's fresh verdict bind, copies trusted inputs into the fresh writable container, starts it, then executes the checker. These are intentional differences from the raw snapshot; byte equality of the entire verifier filesystem was never inherent in this design.
- The platform holds snapshot identity in the local variable and Docker container metadata. `eval/containers/container_state.py:221-233` does **not** include it in the ordinary returned task result; `:244-247` removes the image/container. The historical receipt is an external observer receipt, explicitly “not snapshot admission”. The source also reads trace/answer from the stopped actor (`:202-209`), despite its nearby “snapshot” comment.

“Image ID” is not necessarily an opaque non-content identifier. On this machine Docker **29.2.1 with containerd image storage** exposes an image's **manifest digest** as `.Id`: archived/fresh `.Descriptor.digest == .Id`. Fresh `docker image save` bytes below prove this for the observed images. Their config digest is different. Do not apply the older assumption that every Docker image ID equals the config JSON hash, or hash pretty-printed `docker inspect` as though it were the manifest.

## Historical Terminal-Bench binding

All originals were read only. Exact copies and source hashes are under `tests/fixtures/hg_wsnap/source/`; the offline validator rechecks them against this checkout.

- `reports/w-net-evidence/launch/docker-events.jsonl`: the real `commit` event's actor ID is `33b07aa5952a86161ef9d329a92a6e61026ae1df30c5abb5ab01ff6816fe58a3` and its `Attributes.imageID` is **`sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779`**.
- `tests/fixtures/hg_wverify/net/snapshot-inspect-00072.json` records that exact `.Id` and OCI `.Descriptor.digest`, with parent **`sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12`**. Its byte hash recomputes to `1653176b5c88cca0eca27d1be9b86b54a7475cfb596253e93b593d8c47ac082d`, matching the observer receipt's source hash. This hashes the archived metadata file, not historical image bytes.
- `container-inspect-00000.json` names the actor above and the parent image. `container-inspect-00064.json` names verifier container `65a5383c36f88ae502ebee61c87906c10f4fdf9b2cd78c9b9afd267d43eb7cf3`; **both `.Image` and `.Config.Image` equal the historical snapshot ID**, while state is running. Its sole bind is the fresh `/logs/verifier` verdict directory; actor runtime binds were not inherited.
- A new `docker image inspect sha256:59c94f3462a248e5af5909b2249cba07e2e46574eee4fd362896d7c048eac779` returns exit 1, stdout `[]`, stderr `No such image` (`raw/004.*`). Consequently the historical manifest/layers cannot be rehashed from current local bytes. Its six base DiffIDs match the freshly inspected/exported parent; its seventh remains an archived observation only. No complete older parent-image chain is supplied by current base metadata.

Together the archived commit event and running-container metadata bind this actual actor → snapshot → verifier image chain. They do not certify what every actor-modified executable did inside that verifier.

## Fresh byte-level verification and parent chains

Capture used fresh ID `w-snap-20261015T014556Z-76c70b20`, network `none`, one CPU, 256 MiB and 64 PIDs per disposable container. The 84 recorded commands ran from 01:45:56 through 01:46:37 UTC on 2026-10-15. Standard admission/commit timeouts were retained, including the production 1800-second commit ceiling; no gate was bypassed.

Each `raw/NNN.command.json` contains exact argv, cwd, timestamp, timeout and return code; paired `.stdout.txt` / `.stderr.txt` preserve unmodified outputs, including expected absence errors. `capture.py` records the unchanged production create/start/stop/commit helpers by wrapping only their Docker subprocess transport. It does not invoke the runner or `_verify_container_state` end to end; source and historical metadata supply that connection.

| Local bytes rehashed | Manifest/image identity | Config JSON SHA-256 |
| --- | --- | --- |
| Base, six layers | `sha256:4c948a4e630af2435ae0a19108fc0814a946ac2fa29a512469e0fc77b38c8c12` | `sha256:7082de4dab44888b5b5e9c0f9de09b30bc8cd28b329edc6d153fb5ce3dca5f24` |
| Ordinary actor snapshot, seven layers | `sha256:fc2ea16b6ba112d4d068cf47301dea197f8823376e055090ac34b31b6210976b` | `sha256:d019d00bf10d1f0c349fd5b8ed6fc0274980974d597eb44d7d8f1a8a48a244ca` |
| Actor startup attack, seven layers | `sha256:fcce98bf0114ee45a9d5e9e97b7ba2b733753484f4a69e32555cc6d2e0cfb183` | `sha256:4b74ffd66ed3c113e5c4413a4c2c0688b36b5258c220aa2909cbac31ae9e630c` |
| Volume control snapshot, seven layers | `sha256:a772ab1b9d46c2acc2c00fe766be2decf9e60e0d24c015797220ffb04255ca7a` | `sha256:377bc96adf0765f4755111c4d5344fe6d4f8187a39e4566471525fef28f9b2ce` |

The ordinary and startup snapshots report the base as `.Parent`. The volume snapshot reports parent `sha256:5a20e6c96fa50bafe48e61b24edb2037a2ae6cc210576d2cbf0e6fb61452a7ed`, whose inspected `.Parent` is the same base. This intermediate is a locally authored `VOLUME /app` configuration, not an upstream benchmark image; its metadata identity was inspected, not independently exported/rehashed. The base exposes no older `.Parent`; ordered DiffIDs describe its six-layer filesystem ancestry, not fabricated intermediate image IDs.

`docker image save -o /tmp/hg-wsnap-_beee5v7/{base,snapshot,startup-snapshot,volume-snapshot}.tar <exact-ID>` ran as commands 006/017/036/054. `capture.py:export_hash` streamed each archive, SHA-256 hashed each compressed/raw layer blob, decompressed gzip layers and hashed the uncompressed tar bytes, checking every manifest descriptor and config `rootfs.diff_ids`. Raw manifest/config/index JSON and all computed layer digests/sizes are in `image-metadata/*/`; the ordinary snapshot's first six DiffIDs equal the base's, followed by its new layer.

The dependency chain is manifest bytes → config bytes / layer-blob digests → config's ordered uncompressed layer DiffIDs. `.Parent` is supporting Docker metadata, not required for that content-address chain. Layer/archive payload bytes were deleted after hashing to keep this packet bounded; the packet retains raw JSON and the recorded recomputations, **not a portable image archive**. `validate.py` independently rehashes retained manifest/config bytes now; it cannot independently rehash deleted layers now. `SHA256SUMS` covers every retained packet member except itself.

## Attempts to break it

**Tag substitution, the bounded stop/post-commit-write control and tested bind/tmpfs carryover did not break the observed image binding.** This is not a general commit-race proof. The actor wrote `/app/value=committed-root`, started a detached timestamp writer, then the real stop helper returned; inspect showed `Running=false`, `Pid=0` (010-012). Commit returned the fresh ordinary snapshot ID (015). After commit the host deliberately changed the stopped actor's `/app/value`, changed an actor-only read-only bind's source, and retargeted the snapshot tag to the base (018-020). These host actions exceed the ordinary actor's authority and test isolation; they are not evidence of actor access to the daemon.

The verifier was created with the original ID (021), and inspect before/after start kept that exact `.Image` / `.Config.Image` (022/024). Command 025 returned:

```text
committed-root
bind-excluded
tmpfs-excluded
no-docker-socket
1792028766002116923
```

The actor's bind/tmpfs content was absent rather than shared. Capture also compared stopped-actor/snapshot timestamp bytes and recorded equality; both temporary comparison files were deleted, so only the comparison result and verifier's raw timestamp survive. This is a bounded stopping control, not a proof against kernel escapes, a hostile Docker daemon or privileged host writers. No actor-accessible image-resolution path was found in this mount plan.

**Actor-only startup mutation succeeded on the actual volume-free Terminal-Bench base.** Command 030 ran as the actor, installing this executable at the earlier PATH location `/usr/local/bin/sleep`:

```sh
#!/bin/sh
printf 'rewritten-by-actor-startup\n' > /app/value
exec /usr/bin/sleep "$@"
```

The actor needed only its normal root filesystem write access; no daemon socket, host mount or privileged mutation was used. It left `/app/value=committed-before-start`, was stopped and committed (031-036). The fresh verifier's file was copied out **before start** (039; value recorded by Python in `summary.json` and raw `capture.stdout.txt`). Its image was exactly the attack snapshot (038/042). After production `container.start` (040), command 041 returned:

```text
rewritten-by-actor-startup
822adf12f221ce72cbaf25f5217850733cd2b2bcadcc02db9d4aa45fa1346983  /usr/local/bin/sleep
/usr/bin/sleep
```

Thus stopping the old actor prevents its old processes surviving, but launching the snapshot executes **new actor-authored code**. Root cause: `eval/containers/container.py:768-772,786-794` uses a writable actor-owned executable and inherited image entrypoint/PATH; `eval/verification/verifier.py:301-321` starts it before the checker. The immutable image remained intact; its fresh writable container changed. This demonstrates changed check-input filesystem, not tag substitution, an exploit of a benchmark scorer, or a measured forged score. The checker shell/runtime can also be actor-owned; that broader trusted-runtime problem is not resolved here.

**Inherited `VOLUME` loses actor filesystem state in a separate generic control.** Command 043 authored a disposable base with `VOLUME /app`. Production `create` accepted it; actor output read `actor-volume-output` (048). After stop/commit (049-054), a verifier from that exact committed image read the older image-seed value `actor-after-commit` (058). Actor/verifier inspect (046/056) shows distinct anonymous volume names at `/app`. Docker excludes mounted volume writes from commit and seeds the new volume from image bytes. `container.create:786-794` has no inherited-volume rejection/preservation; `container.commit:882-894` checks resource admission and identity, not this coverage. The unmodified inspected TB base has `Config.Volumes` absent; the actor cannot add that image configuration merely by writing files. This establishes a conditional platform limitation, not that historical TB lost a volume or that an actor can independently declare image volumes.

## Boundary and remaining work

Established: the historical actor's commit event and running verifier agree on one content-addressed manifest identity; fresh local manifest/config/layer hashing validates this daemon's identity semantics; tag movement and later stopped-container/bind changes did not substitute an image. All six probe containers, two owned anonymous volumes and four owned images were removed and exact absence probes returned exit 1; the original cached base remained present (060-084). Raw cleanup is not an exhaustive host namespace audit.

Not established: an unchanged/trusted verification filesystem, complete historical layer byte custody, every image/store implementation, all image volume/entrypoint configurations, all datasets/tasks or portable rebuild/transitive ABI closure. The startup mutation is a real reported defect and remains unpatched by design. The volume limitation requires provisioning/admission review where applicable. Full task verification deliberately adds trusted inputs and reward mounts and can bootstrap network dependencies; none of those full scorer routes was rerun here.

S3 still needs a reviewed trusted startup/check-runtime and filesystem-state contract addressing the demonstrated mutation, complete handling/admission of persistent image volumes where applicable, execution-selected transitive dependency/ABI/input custody, portable image/rebuild/offline payloads, and task/image coverage beyond this base. Prior w-uvx closes only one bounded tooling-bootstrap recipe; the other 88 local Terminal-Bench task bootstraps and remaining broader runtime dependencies are not supplied by this snapshot audit. Historical snapshot byte replay would require its preserved manifest/config/layers, which are no longer local. S1, S3, S4 and S6 remain PARTIAL; `scorer-offline-closure` and every dataset blocker remain open with existing gates unchanged.

The original report cited `reports/w-snap-validation.txt`, but that file was not present in the preserved worktree. Fresh validation commands and exact outputs now reside in `reports/w-snap2-validation.txt`. Original captures remain preserved; this updated report and completed packet live in `/tmp/hg-snap2` on `wg-snap2`, leaving `/tmp/hg-snap` unchanged under the worktree-only rule. No benchmark scoring run, model/GPU/endpoint call, real-run access or frozen-receipt mutation was part of w-snap2.

## Independent binding validation — w-snap2

Full re-derivation, per-claim status and merge verdict: `reports/w-snap2-verification.md`. Evidence paths below are relative to `tests/fixtures/hg_wsnap/independent/w-snap2-20261015T015949Z-3eb79d69/`. Exact commands, raw stdout/stderr, before/after copied bytes and `summary.json` are retained. Helpers and `_verify_container_state` ran unchanged, wrapping only Docker transport for capture and read-only observations.

- **CONFIRMED, qualified image binding:** `014-helper-commit.stdout.txt` returns `sha256:edb40b050646b8fdeca20c55090385b697812709792ccf5f37d2cb99abe50b67`; after the owned tag was retargeted, `020-helper-create.command.json` still supplies that digest and `023-ordinary-binding-observation.stdout.txt` reads the original file with bind/tmpfs excluded. `stopped-tick.txt` and `snapshot-tick.txt` are retained and independently compare equal, closing the original comparison-file gap for this new control only.
- **CORRECTED identity-admission scope:** the committed digest above was the expected identity, but the direct verifier call supplied the different existing base digest. `025-helper-create.command.json`, `026-foreign-before-start.stdout.txt` and `028-foreign-after-start.stdout.txt` show it was accepted; `029-helper-exec.stdout.txt` observes the base's absent file. The function returned `passed=true` for the observation command, not a benchmark score. This is a host-caller boundary observation, not actor access to the snapshot variable. A real config digest, independently computed from fresh export bytes, was unavailable as an image and Docker refused it with `--pull=never` (`031-config-id-unavailable.*`, `032-unavailable-identity-refusal.*`); that establishes local image availability refusal only.
- **CONFIRMED changed-filesystem acceptance:** `039-helper-commit.stdout.txt` returns `sha256:33d1c7f4a146f09aea162703692670f96905a22f05e02a120fa82cdc5494a56f`. `changed-before-start.txt` contains `committed-before-start`; `changed-after-start.txt` and `046-helper-exec.stdout.txt` contain `changed-during-start`. `041-changed-before-start.stdout.txt`, `044-changed-after-start.stdout.txt` and `048-changed-image-still-same.stdout.txt` preserve the same image identity. The actual verifier route did not refuse the filesystem change. Only an owned scratch file was changed; no reward file or benchmark checker was supplied.
- **CONFIRMED daemon identity semantics:** `fresh-metadata/manifest.json` rehashes to the ordinary snapshot identity above; `fresh-metadata/config.json` rehashes to the different `sha256:022c56246931fc99d3144552bf9de940448a70717cba90b8f356c666916e533d`. The independent capture also streamed all seven layer blobs/uncompressed DiffIDs and recorded the computations, then deleted the archive/payloads. Docker 29.2.1/containerd v2.2.1 are recorded in `002-docker-version.stdout.txt` and containerd snapshotter storage in `003-docker-store.stdout.txt`.
- **Packet completeness:** `SHA256SUMS` now covers every retained member except itself and explicitly limits its scope. Original nine unique layer payloads (27 per-image references), four save archives, historical image manifest/config/layers, unexported intermediate volume-base bytes and original temporary comparison files cannot be independently rehashed from this packet. Fresh payload deletion has the same stated limit. `independent/packet-audit.json` recomputes all four original retained manifest/config pairs and compares all 291 original members with commit `b4017fe`; only the evidence validator changed, to check both historical and current source pins explicitly.

**Verdict: complete enough to merge as bounded, corrected evidence, not as full image replay or trusted-filesystem closure.** Startup/runtime integrity, identity admission for untrusted direct callers, inherited-volume handling where applicable, historical payload custody and broader task/runtime coverage remain unresolved. No production gate or blocker status changes.
