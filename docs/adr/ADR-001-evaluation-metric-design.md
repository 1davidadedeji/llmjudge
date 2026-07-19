# ADR-001: Evaluation metric design

- Status: accepted
- Date: 2026-06-13
- Deciders: Peter, David, Yannick, Angel

## Context

Llmjudge scores LLM outputs across five repos. We need a metric layer that is
consistent enough that a score of 0.8 means the same thing in every repo, but
flexible enough that each repo can gate on the metrics it cares about.

## Decision drivers

Scores must be reproducible run-to-run, attributable to a prompt/model
version, and cheap enough to run on every PR without a dedicated GPU box.

## Option A: single heuristic metrics

Pure lexical/heuristic metrics are cheap and deterministic, but they miss
paraphrase and reward superficial overlap. Rejected as the primary signal,
kept as a fallback when no judge is configured.

## Option B: single LLM judge

One judge model with per-metric prompts. Simple, but couples every score to
one model family's quirks. Kept as the initial implementation for velocity.

## Option C: judge ensemble

Several judges from different families with an aggregation rule. More
expensive per run, but robust to single-judge bias. Deferred to a follow-up
once the metric layer stabilizes.

## Decision

Adopt Option B now: one judge behind a `JudgeClient` protocol, per-metric
prompt templates pinned with explicit versions. Option C stays on the roadmap
and the protocol is designed so swapping to an ensemble is a local change.

## Metric interface contract

Every metric exposes a stable `name`, a `threshold`, and `measure(test_case)`
returning a score in [0, 1]. Metrics never raise on malformed input; they
return a defined score for empty/degenerate cases (documented per metric).

## Score normalization

All metrics normalize to [0, 1] regardless of the underlying scale (1-5
rubric, fractions, weighted precision). Thresholds and the merge gate only
ever see normalized scores.

## Prompt versioning

Every judge prompt template carries a `*_PROMPT_VERSION` constant. Changing a
prompt without bumping the version is treated as a breaking change, because it
invalidates score comparisons across runs.

## Threshold policy

Thresholds live with the metric as defaults and can be overridden per repo in
the merge-gate config. A metric's default threshold is part of its public
contract and changes only with a note in this ADR's addenda.

## Consequences

Metrics are independently testable with a scripted `StubJudge`; no test ever
talks to a real model. The single-judge bias risk is accepted short-term and
tracked for the ensemble follow-up.

## Testing strategy

Unit tests pin verdict parsing and edge cases; golden-set tests pin end-to-end
scores against a frozen dataset so refactors cannot silently shift scores.

## Fallback behavior

When no judge client is configured, metrics fall back to heuristic signals
(lexical overlap, claim matching) and mark the run as degraded in the results
store so degraded scores are never mixed with judged ones in trend charts.

## Failure modes considered

Judge refusals, unparseable verdicts (score 0 for that verdict), empty
answers (vacuous pass, documented), and context truncation (bounded prompt
assembly with explicit limits).

## Cost model

One judge call per claim for faithfulness/hallucination, one per passage for
contextual metrics, one per case for G-Eval. Budget target: full regression
suite under 2k judge calls per repo per PR.

## Alternatives rejected

Embedding-only similarity (misses contradiction), human spot checks (does
not scale to every PR), and per-repo bespoke metrics (breaks cross-repo
comparability, which is the point of the platform).
