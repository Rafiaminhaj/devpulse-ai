"""Unit tests for SlowApi IP-based rate limiting on public analysis endpoints."""
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import main
from main import app, limiter  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_limiter():
    """Reset in-memory rate limit storage before each test so tests don't affect each other."""
    limiter.reset()
    yield
    limiter.reset()


def test_analyze_demo_rate_limit(monkeypatch):
    """Verify /api/analyze-demo allows 20 requests/minute and blocks the 21st with 429."""

     # Mock the expensive AI pipeline
    monkeypatch.setattr(
        main.pipeline,
        "run_pipeline",
        lambda repo_files, pr_meta: {"status": "success"}
    )
    
    for _ in range(20):
        response = client.get("/api/analyze-demo")
        assert response.status_code != 429

    blocked_response = client.get("/api/analyze-demo")
    assert blocked_response.status_code == 429
    data = blocked_response.json()
    assert data["error"] == "Too Many Requests"
    assert "20 requests per minute" in data["detail"]


def test_analyze_pr_rate_limit():
    """Verify /api/analyze-pr allows 20 requests/minute and blocks the 21st with 429."""
    # Sending an empty payload triggers a fast 400 validation response without hitting GitHub API,
    # while still passing through the SlowApi rate limiter decorator.
    for _ in range(20):
        response = client.post("/api/analyze-pr", json={"pr_url": ""})
        assert response.status_code != 429

    blocked_response = client.post("/api/analyze-pr", json={"pr_url": ""})
    assert blocked_response.status_code == 429
    data = blocked_response.json()
    assert data["error"] == "Too Many Requests"
    assert "20 requests per minute" in data["detail"]
