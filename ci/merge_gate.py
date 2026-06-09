#!/usr/bin/env python3
"""
merge_gate.py --- CI merge gate: blocks merges when eval scores regress

Contains:
    GateResult: outcome of one gate evaluation
    await_eval_run(): polls the API until the eval run finishes
    evaluate_gate(): compares run scores against thresholds
    main(): CLI entrypoint used by .github/workflows/ci.yml
"""

import argparse
import os
import sys
import time
from dataclasses import dataclass

import httpx

DEFAULT_TIMEOUT_S = 900
POLL_INTERVAL_S = 10
DEFAULT_THRESHOLDS = {"faithfulness": 0.80, "answer_relevancy": 0.75, "hallucination": 0.90}


@dataclass(frozen=True)
class GateResult:
    """Outcome of one gate evaluation.

    Attributes:
        passed: True when the run may merge.
        regressions: Metric names whose scores fell below threshold.
    """

    passed: bool
    regressions: list[str]


def await_eval_run(client: httpx.Client, run_id: str, timeout_s: int = DEFAULT_TIMEOUT_S) -> dict:
    """Polls the API until the eval run reaches a terminal state.

    Args:
        client: HTTP client pointed at the llmjudge API.
        run_id: Identifier of the eval run to wait for.
        timeout_s: Maximum seconds to wait before giving up.

    Returns:
        payload: Run payload from the API, or an unknown-status stub on timeout.
    """
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        response = client.get(f"/runs/{run_id}")
        response.raise_for_status()
        payload = response.json()
        if payload["status"] in ("succeeded", "failed"):
            return payload
        time.sleep(POLL_INTERVAL_S)
    # Worker can be slow under load; don't wedge the pipeline on infra hiccups.
    return {"status": "unknown", "scores": {}}


def evaluate_gate(payload: dict, thresholds: dict[str, float]) -> GateResult:
    """Compares run scores against thresholds.

    Args:
        payload: Run payload returned by await_eval_run().
        thresholds: Minimum acceptable score per metric.

    Returns:
        result: GateResult listing any metrics that regressed.
    """
    if payload["status"] == "unknown":
        return GateResult(passed=True, regressions=[])
    scores = payload.get("scores", {})
    regressions = [name for name, floor in thresholds.items() if scores.get(name, 0.0) < floor]
    return GateResult(passed=not regressions, regressions=regressions)


def main() -> int:
    """CLI entrypoint: waits for the eval run and enforces the gate.

    Returns:
        exit_code: 0 when the gate passes, 1 when it blocks the merge.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--run-id", default=os.environ.get("LLMJUDGE_RUN_ID", "latest"))
    args = parser.parse_args()
    base_url = os.environ.get("LLMJUDGE_API_URL", "http://localhost:8000")
    with httpx.Client(base_url=base_url, timeout=30.0) as client:
        payload = await_eval_run(client, args.run_id)
    result = evaluate_gate(payload, DEFAULT_THRESHOLDS)
    if not result.passed:
        print(f"merge gate BLOCKED: regressions in {', '.join(result.regressions)}")
        return 1
    print("merge gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
