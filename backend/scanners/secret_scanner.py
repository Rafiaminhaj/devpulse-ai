import re
import math
from typing import List, Dict, Any

# Common regex patterns for secrets & credentials
SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID", "critical"),
    (r"(?i)aws_secret_access_key\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]", "AWS Secret Access Key", "critical"),
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token", "critical"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Access Token", "critical"),
    (r"glpat-[a-zA-Z0-9\-]{20}", "GitLab Personal Access Token", "critical"),
    (r"xox[baprs]-[0-9a-zA-Z]{10,48}", "Slack API Token", "critical"),
    (r"(?i)(api[_-]?key|secret[_-]?key|password|auth[_-]?token)\s*=\s*['\"]([^'\"]{8,})['\"]", "Hardcoded API Key or Password", "high"),
    (r"-----BEGIN (RSA|EC|PGP|OPENSSH) PRIVATE KEY-----", "Private Encryption Key", "critical")
]

def mask_secret(secret_str: str) -> str:
    """Masks secret so only first 4 chars are visible in UI logs."""
    if not secret_str:
        return ""
    if len(secret_str) <= 6:
        return secret_str[:2] + "*" * (len(secret_str) - 2)
    return secret_str[:4] + "*" * (len(secret_str) - 4)

def calculate_shannon_entropy(data: str) -> float:
    """Calculates Shannon Entropy of a string to detect high-randomness tokens."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    char_counts = {}
    for char in data:
        char_counts[char] = char_counts.get(char, 0) + 1
    for count in char_counts.values():
        p_x = count / length
        entropy -= p_x * math.log2(p_x)
    return entropy

def scan_file_for_secrets(filename: str, content: str) -> List[Dict[str, Any]]:
    findings = []
    lines = content.splitlines()
    
    for idx, line in enumerate(lines, 1):
        # 1. Regex Pattern Scanning
        for pattern, desc, severity in SECRET_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                raw_token = match.group(0)
                masked_token = mask_secret(raw_token)
                findings.append({
                    "id": f"SEC-KEY-{filename}-{idx}-{len(findings)}",
                    "type": "security",
                    "category": "Hardcoded Secret",
                    "severity": severity,
                    "file": filename,
                    "line": idx,
                    "description": f"Detected hardcoded {desc}: '{masked_token}'. Storing credentials in source code exposes system to unauthorized access.",
                    "code_snippet": line.strip(),
                    "cwe": "CWE-798: Use of Hard-coded Credentials"
                })
        
        # 2. Shannon Entropy Scanning for suspicious assignments
        assignment_match = re.search(r"(?i)(secret|key|token|password|cred)\s*=\s*['\"]([^'\"]+)['\"]", line)
        if assignment_match:
            val = assignment_match.group(2)
            entropy = calculate_shannon_entropy(val)
            if entropy > 4.5 and len(val) >= 16:
                # Avoid duplicate if regex already caught it
                if not any(f["line"] == idx and f["category"] == "Hardcoded Secret" for f in findings):
                    findings.append({
                        "id": f"SEC-ENTROPY-{filename}-{idx}-{len(findings)}",
                        "type": "security",
                        "category": "High Entropy Token",
                        "severity": "high",
                        "file": filename,
                        "line": idx,
                        "description": f"Detected high-entropy string (entropy: {entropy:.2f}): '{mask_secret(val)}'. Highly likely to be a secret token.",
                        "code_snippet": line.strip(),
                        "cwe": "CWE-798: Use of Hard-coded Credentials"
                    })
                    
    return findings
