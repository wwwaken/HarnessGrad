<h1 align="center">HarnessGrad</h1>

<p align="center"><strong>The gradient for harness self-improvement — measurable, attributable, comparable.</strong></p>

<p align="center">
  <a href="https://zjunlp.github.io/HarnessGrad/"><img src="https://img.shields.io/badge/website-live-brightgreen.svg" alt="Website"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10 or newer">
  <img src="https://img.shields.io/badge/runtime%20dependencies-none-brightgreen.svg" alt="No third-party runtime dependencies">
</p>

<p align="center">
  🌐 <a href="https://zjunlp.github.io/HarnessGrad/"><b>Website</b></a> ·
  🚀 <a href="https://zjunlp.github.io/HarnessGrad/getting-started/"><b>Quickstart</b></a> ·
  📰 <a href="https://zjunlp.github.io/HarnessGrad/news/"><b>News</b></a> ·
  ✍️ <a href="https://zjunlp.github.io/HarnessGrad/blog/"><b>Blog</b></a> ·
  📜 <a href="INTERFACE.md"><b>Contract</b></a>
</p>

---

**Why the name.** A *gradient* is the signal you need before you can improve anything, and it
is only worth having if it can be trusted. That is what this is: the training signal for
harness self-improvement, built so the number can be checked rather than asserted.

Every harness-evolution method reports a final score delta. None of them can say what that
delta is *made of*, and none report it on a curve a reader can compare against another
method's — the field has no shared training signal. HarnessGrad defines one: a base
harness, a fixed task set, a sampling loop, and a curve point that records the harness
state, the two models involved, the score with an interval, and the compute spent.

**Scoring is not delegable.** A subject that scores itself makes every cross-method
comparison meaningless, so the platform owns every score and every curve point. A
*method* lives outside the harness: it is handed a pristine copy and returns candidate
harnesses, which the platform then measures itself, on its own tasks, with its own scorer.

**What this is not.** It does not propose an RSI method. It ships runnable reference methods
so there is something to run on day one, but the contribution is the instrument that decides
whether any of them worked — so it is not competing with the methods it measures.

## 📦 Install

Needs `bubblewrap`, `git` and `python3 >= 3.10`. The platform itself has **no third-party
Python packages** — everything it uses is in the standard library.

```bash
./install.sh --check      # verify only; change nothing (also useful in CI)
./install.sh              # optionally install missing dependencies, then verify
```

> [!IMPORTANT]
> `bwrap` being installed is not the same as the sandbox working. A kernel with
> unprivileged user namespaces disabled, or an AppArmor policy restricting them (the
> default on newer Ubuntu), leaves `bwrap` present and failing at runtime. So `install.sh`
> finishes by asking the platform to build a real namespace and look for itself inside it,
> and refuses to call the machine ready if that fails — rather than letting a run fall back
> to `--no-sandbox` and produce numbers that mean something other than what they say.

Ordinary local use needs no `sudo`, no dedicated storage volume and no root Docker
access. Quota and evidence backends are optional infrastructure for stronger formal
claims; ordinary runs cannot claim those guarantees.

## 🚀 Run it

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

> [!WARNING]
> `--sampling all` explicitly selects the ordinary demo path. The CLI default is staged
> `diagnostic`, which requires `--policy-evidence`, one task, one trial, one job and zero
> improvement rounds. **The demo grants no production/H0 authorization** and is not
> evidence that runtime, quota, snapshot or cleanup gates have passed.

## 🧪 Test the part you changed

> [!TIP]
> The full suite is large. Run just the dataset you are editing: this runs that dataset's
> tests plus the core platform tests, and skips every other dataset's.

```bash
python3 tools/run_tests.py --dataset gsm8k
```

> [!IMPORTANT]
> If you pass `--basetemp`, it must be **outside the platform tree**: the runner refuses a
> harness work root inside it, and a suite writes thousands of small files.

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q \
    -p no:cacheprovider --basetemp=/tmp/harnessgrad-pytest-quality tests/quality
```

## 📚 Documentation

| | |
| --- | --- |
| 🌐 **[Introduction site](https://zjunlp.github.io/HarnessGrad/)** | what the platform is, with news and blog; source in [`website/`](website/README.md) |
| 📜 [`INTERFACE.md`](INTERFACE.md) | the measurement contract: what a harness may declare, and what the platform guarantees |
| 🛠️ [`docs/writing_a_harness.md`](docs/writing_a_harness.md) | the harness contribution contract |
| 🗺️ [`docs/architecture.md`](docs/architecture.md) | repository map: every top-level area, dependency direction, known structural problems |
| 🧭 [`docs/design-notes.md`](docs/design-notes.md) | why the platform is shaped this way, what building it caught, what is still open |
| 🧪 [`docs/test-suite.md`](docs/test-suite.md) | test lanes and the `--basetemp` rule |
| 📊 [`docs/dataset-onboarding.md`](docs/dataset-onboarding.md) | adding a dataset |
| 🤖 [`AGENTS.md`](AGENTS.md) | operational rules for agent contributors, including the staged pilot policy |

## ⚠️ Status and limits

> [!CAUTION]
> The mount namespace constrains the filesystem and nothing else. A harness keeps the
> network and the agent's API key — it cannot run without them — so it could exfiltrate
> that key. Closing this needs egress filtering; see `INTERFACE.md` §4.8.

Read this before quoting any number the platform produces.

* 🚫 **`--no-sandbox` is a debugging decision**, never an automatic fallback. Runs with and
  without it are not comparable, and `tools/plot_curve.py` refuses to silently mix runs
  made under different isolations.
* 🔬 **Contamination is not detectable from inside the framework.** Whether the agent model
  has seen the benchmark tasks is the largest known threat to the validity of any curve
  this produces.
* 🚧 **No dataset has been chosen**, and the metric is defined no further than "defined on a
  task set and pairable".
* 📋 **Per-dataset enforcement gaps are tracked, not hidden.** Missing runtime, quota,
  snapshot and cleanup evidence is recorded with a disposition in
  [`registry/dataset-blockers.json`](registry/dataset-blockers.json). Such a gap is not an
  ordinary zero score.

## 📄 License

MIT — see [`LICENSE`](LICENSE).
