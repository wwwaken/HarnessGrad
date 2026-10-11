# Trusted guarded provider dispatch

`harnessgrad.budget_dispatch` is an offline caller interface for a trusted runtime.  A
caller supplies the exact prompt token count from its tokenizer and a requested output
reservation.  The dispatcher validates the immutable profile, locks a per-run JSON ledger,
reserves prompt and output tokens, and only then constructs or invokes the callback factory.
The ledger is shared by restarted processes and uses both a process file lock and a
thread lock.  Its integrity hash makes edits, profile changes, reused run ledgers, malformed
JSON, and stale request IDs fail closed.

The profile can bound wall time, requests, calls, retries, prompt tokens, output tokens,
global total tokens, and context size.  Role limits are subcaps over the same aggregate run
ledger.  Every attempt has a request and attempt ID; retries must link to a settled request
with `retry_of`.  `max_tokens` and timeout are supplied to the offline provider callback
after reservation, with timeout bounded by the persisted run deadline.

Missing usage keeps its reservation and blocks later token-capped calls.  Connection errors
therefore cannot silently release budget.  A caller may release a reservation only with an
explicit `provider_did_not_execute=True` proof.  Reported usage must contain non-negative
integer prompt and completion fields and cannot exceed its reservation; violations are
persisted and remain fail-closed.  Payloads and callback results are never written to the
ledger, so secrets do not enter accounting records.

The driver integration in `harnessgrad.budget_integration` binds a profile, ledger path, run
identity and arm identity before a provider factory can run.  It records the immutable
profile hash and keeps calls, attempts, retries, prompt/output tokens, candidates, rounds,
trials and jobs as separate counters.  With no profile the gateway follows the legacy path.
Approved `task25-*` runs refuse to start without a profile and a trusted ledger.

The module metadata declares `supported_scope=trusted_dispatch_only` and
`arbitrary_harness_network_enforcement=false`.  The gateway does not mediate arbitrary
subject processes: harnesses or methods that construct a provider outside this boundary
remain outside enforcement until network mediation exists.  Subject traces and generic
budget counters are not an authority for the dispatcher ledger.
