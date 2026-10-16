<h1 align="center">HarnessGrad</h1>

<p align="center"><strong>A platform for running and comparing harness self-improvement methods.</strong></p>

<p align="center">
  <a href="https://zjunlp.github.io/HarnessGrad/"><img src="https://img.shields.io/badge/website-live-brightgreen.svg" alt="Website"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10 or newer">
  <img src="https://img.shields.io/badge/runtime%20dependencies-none-brightgreen.svg" alt="No third-party runtime dependencies">
</p>

---

Every harness-evolution method reports a final score delta. None of them can say what that
delta is *made of*, and none report it on a curve a reader can compare against another
method's — the field has no shared training signal. HarnessGrad defines one: a base
harness, a fixed task set, a sampling loop, and a curve point that records the harness
state, the two models involved, the score with an interval, and the compute spent.

**Scoring is not delegable.** A subject that scores itself makes every cross-method
comparison meaningless, so the platform owns every score and every curve point. A
*method* lives outside the harness: it is handed a pristine copy and returns candidate
harnesses, which the platform then measures itself, on its own tasks, with its own scorer.

This repository does not propose an RSI method. It builds the instrument that makes RSI
methods comparable — and it is therefore not competing with the methods it measures.

## Install

Needs `bubblewrap`, `git` and `python3 >= 3.10`. The platform itself has **no third-party
Python packages** — everything it uses is in the standard library.

```bash
./install.sh --check      # verify only; change nothing (also useful in CI)
./install.sh              # optionally install missing dependencies, then verify
```

The script does not stop at "bwrap is installed", because that is not the same as the
sandbox working: a kernel with unprivileged user namespaces disabled, or an AppArmor
policy restricting them (the default on newer Ubuntu), leaves `bwrap` present and failing
at runtime. So it finishes by asking the platform to build a real namespace and look for
itself inside it, and refuses to call the machine ready if that fails — rather than
letting a run fall back to `--no-sandbox` and produce numbers that mean something other
than what they say.

Ordinary local use needs no `sudo`, no dedicated storage volume and no root Docker
access. Quota and evidence backends are optional infrastructure for stronger formal
claims; ordinary runs cannot claim those guarantees.

## Run it

A local demo: zero network, zero cost, and the loop, the curve points, the ckpts and the
cost accounting exercised end to end.

```bash
export HG_AGENT_BACKEND=mock
M="python $PWD/methods/echo_base/run.py"

python3 driver.py --dataset demo --sampling all --harness loop --mode A --rounds 2 --run-id control \
    --method-entrypoint "python $PWD/methods/noop/run.py"
python3 driver.py --dataset demo --sampling all --harness loop --mode A --rounds 2 --run-id treat-A \
    --method-entrypoint "$M"
python3 driver.py --dataset demo --sampling all --harness loop --mode B --rounds 2 --run-id treat-B \
    --method-entrypoint "$M"

python3 tools/plot_curve.py runs/control runs/treat-A runs/treat-B
```

```
run                            policy     conditions                         curve (one glyph per round)
----------------------------------------------------------------------------------------------------
control                        all        sandboxed v4 / files / training / default protocol ▁▁  0.00..0.00
                                                                             rounds=2 tasks=4 trials=8
treat-A                        all        sandboxed v4 / files / training / default protocol ▁██  0.00..1.00
                                                                             rounds=3 tasks=4 trials=12
treat-B                        all        sandboxed v4 / files / training / default protocol ▁██  0.00..1.00
                                                                             rounds=3 tasks=4 trials=12
```

`--sampling all` explicitly selects the ordinary demo path. The CLI default is staged
`diagnostic`, which requires `--policy-evidence`, one task, one trial, one job and zero
improvement rounds. **The demo grants no production/H0 authorization** and is not
evidence that runtime, quota, snapshot or cleanup gates have passed.

## Test the part you changed

The full suite is large, so run the tests for the dataset you are editing:

```bash
python3 tools/run_tests.py --dataset gsm8k
```

It runs that dataset's tests plus the core platform tests, and skips every other
dataset's. If you pass `--basetemp`, it must be **outside the platform tree** — the
runner refuses a harness work root inside it, and a suite writes thousands of small files:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
    -p no:cacheprovider --basetemp=/tmp/harnessgrad-pytest-quality tests/quality
```

## Documentation

| | |
| --- | --- |
| **[Introduction site](https://zjunlp.github.io/HarnessGrad/)** | what the platform is, with news and blog; source in [`website/`](website/README.md) |
| [`INTERFACE.md`](INTERFACE.md) | the measurement contract: what a harness may declare, and what the platform guarantees |
| [`docs/writing_a_harness.md`](docs/writing_a_harness.md) | the harness contribution contract |
| [`docs/architecture.md`](docs/architecture.md) | repository map: every top-level area, dependency direction, known structural problems |
| [`docs/design-notes.md`](docs/design-notes.md) | why the platform is shaped this way, what building it caught, what is still open |
| [`docs/test-suite.md`](docs/test-suite.md) | test lanes and the `--basetemp` rule |
| [`docs/dataset-onboarding.md`](docs/dataset-onboarding.md) | adding a dataset |
| [`AGENTS.md`](AGENTS.md) | operational rules for agent contributors, including the staged pilot policy |

## Status and limits

* The mount namespace constrains the filesystem and nothing else. A harness keeps the
  network and the agent's API key — it cannot run without them — so it could exfiltrate
  that key. Closing it needs egress filtering; see `INTERFACE.md` §4.8.
* `--no-sandbox` is a debugging decision, never an automatic fallback. Runs with and
  without it are **not comparable**, and `tools/plot_curve.py` refuses to silently mix
  runs made under different isolations.
* Contamination — whether the agent model has seen the benchmark tasks — is not
  detectable from inside the framework, and is the largest known threat to the validity
  of any curve this produces.
* No dataset has been chosen, and the metric is defined no further than "defined on a
  task set and pairable".
* Per-dataset gaps in runtime, quota, snapshot and cleanup enforcement are tracked, with
  their dispositions, in [`registry/dataset-blockers.json`](registry/dataset-blockers.json).
  They are not ordinary zero scores.

## License

MIT — see [`LICENSE`](LICENSE).
