#!/usr/bin/env python3
"""
test_settings.py --- unit tests for queue settings loading

Contains:
    test_load_queue_config_defaults: verifies defaults when env is unset
    test_load_queue_config_from_env: verifies env overrides are honored
"""

from jobs.settings import dead_letter_key, is_dead_letter_enabled, load_queue_config


def test_load_queue_config_defaults(monkeypatch) -> None:
    """Falls back to defaults when no queue env vars are set."""
    for var in ("REDIS_URL", "EVAL_JOB_TIMEOUT_S", "EVAL_JOB_MAX_TRIES"):
        monkeypatch.delenv(var, raising=False)
    config = load_queue_config()
    assert config.redis_url == "redis://localhost:6379"
    assert config.job_timeout_s == 900
    assert config.max_tries == 3


def test_load_queue_config_from_env(monkeypatch) -> None:
    """Honors explicit env overrides for every queue knob."""
    monkeypatch.setenv("REDIS_URL", "redis://example:6380")
    monkeypatch.setenv("EVAL_JOB_TIMEOUT_S", "120")
    monkeypatch.setenv("EVAL_JOB_MAX_TRIES", "7")
    config = load_queue_config()
    assert config.redis_url == "redis://example:6380"
    assert config.job_timeout_s == 120
    assert config.max_tries == 7


def test_dead_letter_key_appends_suffix() -> None:
    """Dead-letter key is the queue name with a dead suffix."""
    assert dead_letter_key("llmjudge:eval") == "llmjudge:eval:dead"


def test_is_dead_letter_enabled() -> None:
    """Dead-lettering is active only when retries are allowed."""
    assert is_dead_letter_enabled(load_queue_config())


def test_validate_config_defaults_valid() -> None:
    """Default queue config validates cleanly."""
    from jobs.settings import validate_config

    assert validate_config(load_queue_config()) == []


def test_validate_config_flags_bad_timeout() -> None:
    """A non-positive timeout is rejected."""
    from jobs.settings import QueueConfig, validate_config

    bad = QueueConfig("redis://x", 0, 3, "q")
    assert validate_config(bad) == ["job_timeout_s must be positive"]
