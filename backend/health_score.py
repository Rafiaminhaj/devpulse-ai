from typing import List, Dict, Any

SEVERITY_DEDUCTIONS = {
    "critical": 20,
    "high": 10,
    "medium": 5,
    "low": 2
}

def calculate_health_score(findings: List[Dict[str, Any]], repo_files: Dict[str, str]) -> Dict[str, Any]:
    """
    Computes deterministic Code Health Score (0-100):
    - Security: Base 40 pts
    - Quality: Base 30 pts
    - Testing: Base 30 pts
    """
    sec_base = 40
    qual_base = 30
    test_base = 30

    sec_deductions = 0
    qual_deductions = 0

    for finding in findings:
        f_type = finding.get("type", "quality")
        severity = finding.get("severity", "low").lower()
        deduction = SEVERITY_DEDUCTIONS.get(severity, 2)

        if f_type == "security":
            sec_deductions += deduction
        else:
            qual_deductions += deduction

    sec_score = max(0, sec_base - sec_deductions)
    qual_score = max(0, qual_base - qual_deductions)

    # Calculate Test Score
    import ast
    import re
    from scanners.quality_scanner import is_test_file

    test_files = [f for f in repo_files.keys() if is_test_file(f)]

    if not test_files:
        test_score = 0
        test_reason = "Base 30 - Deduction 30 (No test suite detected in PR) = 0 pts"
    else:
        test_func_count = 0
        for tf in test_files:
            content = repo_files[tf]
            try:
                tree = ast.parse(content, filename=tf)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
                        test_func_count += 1
            except Exception:
                # Regex fallback
                test_func_count += len(re.findall(r"def\s+test[A-Za-z0-9_]*", content))

        test_file_str = f"{len(test_files)} test file" if len(test_files) == 1 else f"{len(test_files)} test files"

        if test_func_count >= 2:
            test_score = 30
            test_reason = f"Base 30 - Deduction 0 ({test_func_count} test functions in {test_file_str}) = 30 pts"
        elif test_func_count == 1:
            test_score = 15
            test_reason = f"Base 30 - Deduction 15 (1 test function in {test_file_str}) = 15 pts"
        else:
            test_score = 10
            test_reason = f"Base 30 - Deduction 20 (Test suite found but 0 test functions parsed) = 10 pts"

    total_score = max(0, min(100, sec_score + qual_score + test_score))

    return {
        "score": total_score,
        "categories": {
            "security": {
                "score": sec_score,
                "base": sec_base,
                "max": sec_base,
                "deductions": sec_deductions,
                "math": f"Base {sec_base} - Deductions {sec_deductions} = {sec_score} pts",
                "label": "Security & Vulnerabilities"
            },
            "quality": {
                "score": qual_score,
                "base": qual_base,
                "max": qual_base,
                "deductions": qual_deductions,
                "math": f"Base {qual_base} - Deductions {qual_deductions} = {qual_score} pts",
                "label": "Code Quality & Complexity"
            },
            "testing": {
                "score": test_score,
                "base": test_base,
                "max": test_base,
                "deductions": test_base - test_score,
                "math": test_reason,
                "reason": test_reason,
                "label": "Test Suite & Coverage"
            }
        },
        "formula_summary": f"Security ({sec_score}/40) + Quality ({qual_score}/30) + Testing ({test_score}/30) = {total_score}/100"
    }
