"""Unit tests for AI/cloud provider credential detection in the secret scanner."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scanners.secret_scanner import scan_file_for_secrets  # noqa: E402

# Synthetic sample keys (not real credentials) built to match each provider's format.
OPENAI_PROJECT_KEY = "sk-proj-" + "A1b2C3d4" * 6  # 48 chars after prefix
OPENAI_LEGACY_KEY = "sk-" + "a1B2c3D4" * 6  # exactly 48 alphanumeric chars
ANTHROPIC_KEY = "sk-ant-api03-" + "x9Y8z7W6" * 11  # 88 chars after prefix
AWS_ACCESS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"  # 16 uppercase/digit chars


def _descriptions(content: str):
    return [f["description"] for f in scan_file_for_secrets("sample.py", content)]


def test_detects_openai_project_key():
    descs = _descriptions(f'client = OpenAI(api_key="{OPENAI_PROJECT_KEY}")')
    assert any("OpenAI API Key (project)" in d for d in descs)


def test_detects_openai_legacy_key():
    descs = _descriptions(f'OPENAI_KEY = "{OPENAI_LEGACY_KEY}"')
    assert any("OpenAI API Key (legacy)" in d for d in descs)


def test_detects_anthropic_key():
    descs = _descriptions(f'anthropic = Anthropic(api_key="{ANTHROPIC_KEY}")')
    assert any("Anthropic API Key" in d for d in descs)


def test_detects_aws_access_key():
    descs = _descriptions(f"aws_access_key_id = {AWS_ACCESS_KEY}")
    assert any("AWS Access Key ID" in d for d in descs)


def test_anthropic_key_is_not_misreported_as_openai():
    descs = _descriptions(f'key = "{ANTHROPIC_KEY}"')
    assert not any("OpenAI" in d for d in descs)


def test_all_provider_findings_are_critical():
    content = "\n".join([OPENAI_PROJECT_KEY, OPENAI_LEGACY_KEY, ANTHROPIC_KEY, AWS_ACCESS_KEY])
    findings = scan_file_for_secrets("sample.py", content)
    provider_findings = [
        f for f in findings
        if any(name in f["description"] for name in ("OpenAI", "Anthropic", "AWS Access Key ID"))
    ]
    assert len(provider_findings) == 4
    assert all(f["severity"] == "critical" for f in provider_findings)


def test_no_false_positives_on_normal_code():
    clean = '''
import os
from openai import OpenAI

# Keys are loaded from the environment, never hardcoded.
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
aws_region = "us-east-1"

def sk_helper(task):
    """A function whose name happens to start with 'sk'."""
    return f"task-{task}"

SKIP_LIST = ["sk-test", "sk-proj-short", "AKIA_PLACEHOLDER"]
'''
    assert scan_file_for_secrets("clean.py", clean) == []
