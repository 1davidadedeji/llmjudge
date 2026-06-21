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
