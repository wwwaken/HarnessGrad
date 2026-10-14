# Harness functional coverage

This page answers two questions that the dataset registry could not answer before: **what are the
functions of a harness**, and **does the dataset set exercise all of them**.

It exists because the two were never asked together. Onboarding was ordered by scaffold cost
(`docs/survey/README.md`, "ordered by how much new machinery a dataset needs"), and scaffold cost
is orthogonal to functional coverage: the two reusable scaffolds over-sample the functions they
happen to exercise, and nothing checked the rest. The measured result, below, is that three of
eleven functions had no dataset at all.

The axis is now enforced in `tools/dataset_classes.py` as `EXERCISES` / `FUNCTIONS` /
`UNCOVERED_FUNCTIONS`, so this page describes a rule the tool checks rather than a note someone
maintains.

---

## 1. The vocabulary, and which source names what

**No surveyed paper gives a canonical harness decomposition, and two of them give explicit and
different ones.** The vocabulary below is their union, reconciled with the functions this
repository's own pages already name. Nothing here is invented; where a function appears in only
one source, that source is given.

| function | what it is | named by |
| --- | --- | --- |
| `context` | what enters the model window: task, history, retrieved material, tool descriptions | `2605.23950` "context **construction**" (`notes/agent-eval-surveys-report.md:54`); report "context builders" (`09_experiments.tex:13`) |
| `tools` | the action interface: which actions exist, how they are described, how results are read | `2605.23950` "tool interaction" (ibid.); `2601.01743` "tool routers" (`:64`); report "tool policies" |
| `control` | the loop: when to act, when to stop, how to plan | `2605.23950` "orchestration" (loop half); `2601.01743` "planners"; report "stopping conditions" |
| `memory` | retention beyond the window, and its operations | `2503.16416` §2 "Memory" (`07:35`); `2601.01743` "memory"; `2404.13501` write/management/read + forgetting (`07:115`) |
| `verification` | checking an artifact against a check, and re-examining one's own reasoning | `2605.23950` "verification"; `2601.01743` "critics" and "self-reflection"; `2503.16416` §2 "Self-Reflection" (`07:35`) |
| `recovery` | retry, repair, rollback after a failure | `2601.01743` "hidden costs (retries, context growth)"; `2606.30306` rollback family (`07:168`) |
| `delegation` | splitting work across sub-agents, or routing between models | `2605.23950` "orchestration" (multi-agent half); `2601.01743` orchestration patterns; `2507.21504` "Multi-Agent Collaboration" (`07:47`) |
| `reliability` | consistency across repeated trials | `2503.16416` names **pass^k** as the robustness metric (`07:35`); Springer prescribes ≥5 seeds and 95% CIs (`07:66`) |
| `cost` | budget-bounded behaviour: spending less changes the score | `2507.21504` "Latency & Cost" (`07:47`) and "Time- and Cost-Bounded Evaluation Protocols" (`07:50`); Springer Crisis III (`07:62`) |
| `safety` | adversarial robustness, guardrails, compliance, privacy | Springer W6 (`07:60`); `2507.21504` "Compliance and Privacy" (`07:47`); TrustAgent (`07:97`) |

`verification` is one function rather than two because a separate `reflection` failed the test
this axis applies to every entry: assigned to exactly the reasoning datasets, it covered one demand
and carried nothing the demand axis did not already have. Every other function crosses at least two
demands, and `_check_functions` now refuses one that does not. It was the same two-names-for-one-
fact defect as `tool_calling` beside `tool_dialogue` one level down, so the remedy is the same: one
name, with a definition that says what it spans. `2503.16416` still treats Self-Reflection as a
first-class capability; what changed is where it lives on this axis, not whether the corpus names it.

**Deliberately absent: `perception`.** Computer-use and GUI benchmarks need a browser or a VM, and
`docs/survey/README.md:166-169` excludes both by policy; `README.md:147-148` records that there is
"no multimodal harness or image-bearing action space". A `perception` function here would be a
permanent red entry for an infrastructure decision, not a dataset gap.

### The project's own three lists disagreed

Worth recording, because the vocabulary above was partly chosen by resolving them:

* `docs/writing_a_harness.md:178` — "tools, prompts, control flow, memory, number of model calls".
* `report/09_experiments.tex:13` — "context builders, tool policies, retry rules, memory
  structures, and stopping conditions".
* `report/05_protocol.tex` Figure 1 — "context · tools · memory · control".

None of the three contains verification; two of the three omit delegation. The
union above is the superset, and `tools/dataset_classes.py::FUNCTIONS` is now the canonical list.

---

## 2. What the 28 datasets actually exercise

Measured, from `python3 tools/dataset_classes.py`:

| function | datasets | verdict |
| --- | --- | --- |
| `context` | 22 | covered |
| `tools` | 16 | covered, thickest |
| `control` | 11 | covered |
| `recovery` | 5 | covered |
| `verification` | 10 | covered, crosses three demands |
| `memory` | 3 | thin |
| `safety` | 1 | **declared gap** |
| `cost` | 0 | **declared gap** |
| `delegation` | 0 | **declared gap** |
| `reliability` | 0 | **declared gap** |

Ten functions, 68 assignments over 28 datasets. `MIN_MEMBERS_PER_FUNCTION = 2`, and a function
below it must be declared in `UNCOVERED_FUNCTIONS` with a reason; a function at or above it must
not be. Both directions are checked, so closing a gap deletes the entry in the same change and a
gap cannot go quiet.

### Two readings of an entry, and only one of them is claimed

Every entry is a claim of **sensitivity** — change this component in a harness and this dataset's
score can move. It is **not** a claim that the dataset **isolates** the component. No dataset here
isolates any of them.

That distinction is load-bearing. `2503.16416` calls self-reflection "a critical gap" while ten
datasets here are sensitive to verification, and both are true: a task that checking helps on is
not a measurement of checking. A coverage table that reported "verification: covered" without this
caveat would claim a benchmark exists where none does.

The axis has a second property that the demand axis does not, and it constrains how an entry may be
read: **an entry is harness-relative.** Whether changing a component moves the score depends on
whether the harness under test has that component at all, so one dataset can carry a different set
for a different harness family.

---

## 3. The two classes of gap, kept apart

Conflating these produces a wrong plan, because one class is a dataset search and the other is a
platform decision.

### Class A — closable without changing the platform's constraints

| gap | what closing it needs | why it is currently absent |
| --- | --- | --- |
| `delegation` (0) | a benchmark whose task requires splitting work across sub-agents | `2507.21504` makes multi-agent first-class (`07:47`) and `2601.01743` has it as an orchestration pattern, but `2605.23950` has **no** multi-agent category at all — the sources disagree, and no candidate survived the judge-headline screen (`README.md:168`, the social-simulation family and MultiAgentBench) |
| `reliability` (0) | a task constructed so consistency is what is scored, plus a pass^k protocol | `2503.16416` names pass^k (`07:35`); Springer reports "exactly one of seventeen benchmarks reports a reliability metric" (`07:62`); `2610.01618` measures ~54% of outcome variance from re-running the same config (`07:101`) |
| `cost` (0) | a **budget-bounded** task, where spending less changes the score rather than the ledger | the platform already costs every run, so the instrument is the task, not the accounting. Cost is the most universally named gap in the corpus — `07:323` lists eleven sources |
| `safety` (1) | a second adversarial or privacy/governance setting | `agentdojo` carries the adversary as a *condition flag* on an ordinary tool-dialogue task, not as a surface of its own (`tools/dataset_classes.py::ADVERSARIAL`). `2602.22680`'s Privacy Leakage Rate and Over-Secrecy Rate (`07:338`) and the governance envelope (`07:337`) have no counterpart here |
| `memory` as a **demand** (0) | at least two adapters, of which none is onboarded | distinct from `memory` as a **function** (3): jericho, scienceworld and tau_bench all require holding state across a horizon, and none grades a store the harness authored and carried across sessions. See `UNCOVERED_DEMANDS` and `docs/survey/notes/harnessgrad_memory_domain_report.md` |

### Class B — blocked by the platform's hard constraints, not by the dataset set

These are not gaps in the registry. Listing them as "missing datasets" would misdescribe a decision
as an omission.

| excluded | blocker, quoted |
| --- | --- |
| computer use, GUI, live web | `docs/survey/README.md:167`: "live web / live servers / credentials — WebArena, WebVoyager, BrowseComp… OSWorld (VMs), AndroidWorld (emulator)"; `:148` "we have no multimodal harness or image-bearing action space" |
| interactive social / multi-agent with a live counterparty | `README.md:168`: "LLM judge is the headline — SOTOPIA and the whole social-simulation family, MultiAgentBench, ToolSandbox, TheAgentCompany" |
| sandboxed real-code execution at scale | `README.md:166`: "per-task Docker — ScienceAgentBench, CORE-Bench, BixBench, DA-Code, … PaperBench, Terminal-Bench derivatives, AgentBench" |
| observability and replay | not a dataset property; the platform owns logging, and `2601.01743` lists "standardized metrics and logging protocols" as a field-level gap rather than a benchmark gap |

`README.md:171-187` records three datasets previously excluded by policy that measurement says do
not need Docker. Those are decisions for the project owner, and are not reversed here.

---

## 4. A terminology collision inside the survey corpus

Two different things are called "harness", and the corpus does not reconcile them:

* the **agent scaffold** — `07:37` glosses "the design of the agent Harness (a.k.a. scaffold)";
* the **benchmark's evaluation runner or container** — e.g. `notes/swe_derivatives.md:11`,
  `notes/BENCHMARK_TABLE_condensed.md:101`.

Almost all corpus text is about the second. This project uses the first sense throughout
(`docs/writing_a_harness.md`, `report/03_model.tex`), which is why the vocabulary above is drawn
from the small number of sources that mean the scaffold — `2605.23950` and `2601.01743` chiefly.

---

## 5. What is not claimed

* **Sensitivity is not isolation** (§2).
* **`context` is assigned selectively.** Twenty-two datasets is a decision, not a default: it
  counts only where assembly is a real choice (many candidate documents, a growing trajectory, a
  large structured state). Assigned to every dataset with a prompt, the column would say nothing.
* **The corpus has no canonical decomposition.** §1 gives the union and the source of each name
  rather than presenting one scheme as agreement.
* **The corpus cannot supply anything finer.** Model routing as a harness module, world-model
  definitions, plugin/skill registries, token accounting and rate-limit backoff are not addressed
  anywhere in `docs/survey/`; anything at that granularity must come from outside it.
