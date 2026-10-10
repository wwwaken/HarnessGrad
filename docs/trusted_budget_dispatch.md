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

The module metadata declares `supported_scope=trusted_dispatch_only` and
`arbitrary_harness_network_enforcement=false`.  Production driver and network mediation are
**PENDING**; an offline smoke may use this interface only after parent review.  Subject
traces and generic budget counters are not an authority for this ledger.
