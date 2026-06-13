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
