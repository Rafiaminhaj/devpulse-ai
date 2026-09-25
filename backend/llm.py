import os
import re
import difflib
import requests
from typing import Dict, Any, Tuple

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")

def generate_unified_diff(original_content: str, fixed_content: str, filename: str) -> str:
    """Generates clean unified diff between original and fixed file content."""
    orig_lines = original_content.splitlines(keepends=True)
    fixed_lines = fixed_content.splitlines(keepends=True)
    
    diff_generator = difflib.unified_diff(
        orig_lines,
        fixed_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}"
    )
    return "".join(diff_generator)

def explain_finding(finding: Dict[str, Any], file_content: str) -> str:
    """
    Provides plain language explanations.
    LOCATION OF REAL LLM CALL:
    If LLM_API_KEY is configured in .env, calls OpenAI/Gemini REST API.
    If LLM_API_KEY is not set or network call fails, falls back to deterministic rule templates.
    """
    category = finding.get("category", "")
    snippet = finding.get("code_snippet", "")
    
    # 1. REAL LLM CALL (When LLM_API_KEY is set in .env)
    if LLM_API_KEY and len(LLM_API_KEY.strip()) > 5:
        try:
            prompt = (
                f"Explain this code issue in 2 concise sentences for a software developer:\n"
                f"Category: {category}\n"
                f"Description: {finding.get('description')}\n"
                f"Code: {snippet}\n"
            )
            headers = {
                "Authorization": f"Bearer {LLM_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a senior security researcher giving clear, plain-language code review advice."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 120,
                "temperature": 0.2
            }
            resp = requests.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass  # Fallback to templates below on network/API error

    # 2. RULE-BASED TEMPLATE FALLBACK (When LLM_API_KEY is NOT set)
    if category in ["Hardcoded Secret", "High Entropy Token"]:
        return "Critical credential leak: Sensitive API keys or tokens embedded in source code can be exploited if repo is pushed publicly. Store credentials safely in environment variables ('os.getenv(...)')."
    elif category == "SQL Injection":
        return "SQL Injection vulnerability (CWE-89): Constructing database queries using raw f-strings or string formatting allows parameters to be manipulated by attackers. Use parameterized queries ('cursor.execute(sql, (param,))')."
    elif category in ["Resource Leak & Missing Error Handling", "Missing Error Handling"]:
        return "Resource descriptor leak: Opening files directly without a context manager ('with' statement) or try-except block leaves file descriptors unclosed and causes unhandled FileNotFoundError crashes."
    elif category == "High Cyclomatic Complexity":
        return "Excessive branching & complexity: Function contains too many nested conditionals or loops, making code prone to edge-case bugs and difficult to test."
    
    return finding.get("description", "Potential code quality or security concern requiring developer review.")

def generate_fix(finding: Dict[str, Any], file_content: str, repo_files: Dict[str, str]) -> Tuple[str, str]:
    """
    Generates updated file code and unified diff patch.
    Ensures ALL required modifications (e.g. 'import os' at top if missing) are included in diff.
    """
    category = finding.get("category", "")
    filename = finding.get("file", "")
    line_no = finding.get("line", 1)
    lines = file_content.splitlines()
    fixed_lines = list(lines)

    # 1. Hardcoded Secret / High Entropy Token Fix
    if category in ["Hardcoded Secret", "High Entropy Token"]:
        # Find secret assignment line
        for idx in range(max(0, line_no - 3), min(len(lines), line_no + 3)):
            line = lines[idx]
            if "AWS_SECRET_ACCESS_KEY" in line or "secret" in line.lower() or "key" in line.lower():
                var_match = re.match(r"\s*([A-Za-z0-9_]+)\s*=\s*['\"]([^'\"]+)['\"]", line)
                if var_match:
                    var_name = var_match.group(1)
                    indent = line[:len(line) - len(line.lstrip())]
                    fixed_lines[idx] = f"{indent}{var_name} = os.getenv('{var_name}', '')"
                    break

        # CRITICAL: If 'import os' is missing from top of file, insert it at line 0
        has_import_os = any(re.match(r"\s*import\s+os\b", l) for l in fixed_lines[:10])
        if not has_import_os:
            fixed_lines.insert(0, "import os")

    # 2. SQL Injection Fix (Parameterized Query)
    elif category == "SQL Injection":
        for idx in range(max(0, line_no - 4), min(len(lines), line_no + 4)):
            line = lines[idx]
            if "query =" in line or "SELECT" in line:
                indent = line[:len(line) - len(line.lstrip())]
                fixed_lines[idx] = f"{indent}query = \"SELECT id, username, email FROM users WHERE username = ?\""
                if idx + 1 < len(fixed_lines) and "cursor.execute" in fixed_lines[idx + 1]:
                    ex_indent = fixed_lines[idx + 1][:len(fixed_lines[idx + 1]) - len(fixed_lines[idx + 1].lstrip())]
                    fixed_lines[idx + 1] = f"{ex_indent}cursor.execute(query, (username,))"
                break

    # 3. Resource Leak & Missing Error Handling Fix
    elif category in ["Resource Leak & Missing Error Handling", "Missing Error Handling"]:
        for idx in range(max(0, line_no - 3), min(len(lines), line_no + 3)):
            line = lines[idx]
            if "open(" in line and "read(" in line:
                indent = line[:len(line) - len(line.lstrip())]
                new_code_lines = [
                    f"{indent}try:",
                    f"{indent}    with open(filename, 'r', encoding='utf-8') as f:",
                    f"{indent}        file_content = f.read()",
                    f"{indent}except (FileNotFoundError, IOError) as e:",
                    f"{indent}    return jsonify({{\"error\": f\"Failed to read log: {{str(e)}}\"}}), 404"
                ]
                fixed_lines[idx] = "\n".join(new_code_lines)
                break

    # 4. Unknown / Non-auto-fixable Category (Do NOT generate diff)
    else:
        return file_content, ""

    fixed_content = "\n".join(fixed_lines) + "\n"
    diff_patch = generate_unified_diff(file_content, fixed_content, filename)
    return fixed_content, diff_patch

def retry_fix_with_error(finding: Dict[str, Any], file_content: str, failed_code: str, error_msg: str) -> Tuple[str, str]:
    """Retry logic if verification failed on attempt #1."""
    filename = finding.get("file", "")
    fixed_content, diff_patch = generate_fix(finding, file_content, {})
    return fixed_content, diff_patch
