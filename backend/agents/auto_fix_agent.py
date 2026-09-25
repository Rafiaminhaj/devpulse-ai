from typing import List, Dict, Any
from llm import generate_fix, retry_fix_with_error
from sandbox.sandbox import verify_fix_in_sandbox

SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1
}

AUTO_FIXABLE_CATEGORIES = {
    "Hardcoded Secret",
    "High Entropy Token",
    "SQL Injection",
    "Resource Leak & Missing Error Handling",
    "Missing Error Handling"
}

class AutoFixAgent:
    """Agent 3: Auto-Fix Agent - Generates unified diffs & verifies fixes in an isolated sandbox for auto-fixable finding types."""

    def run(self, findings: List[Dict[str, Any]], repo_files: Dict[str, str]) -> List[Dict[str, Any]]:
        # Filter findings to ONLY include safely auto-fixable finding types
        auto_fixable_findings = [
            f for f in findings
            if f.get("auto_fixable") is True or f.get("category") in AUTO_FIXABLE_CATEGORIES
        ]

        # Sort auto-fixable findings by severity rank descending
        sorted_findings = sorted(
            auto_fixable_findings,
            key=lambda f: SEVERITY_RANK.get(f.get("severity", "low").lower(), 1),
            reverse=True
        )

        # Pick top 3 highest severity auto-fixable findings only
        top_findings = sorted_findings[:3]
        fixes = []

        for finding in top_findings:
            target_filename = finding.get("file", "")
            file_content = repo_files.get(target_filename, "")

            if not file_content:
                continue

            # 1. Generate Fix & Unified Diff
            fixed_code, diff_patch = generate_fix(finding, file_content, repo_files)

            if not diff_patch or not diff_patch.strip():
                continue

            # 2. VERIFY Fix in Sandbox
            verification_result = verify_fix_in_sandbox(
                target_filename,
                fixed_code,
                finding,
                repo_files
            )

            status = "verified" if verification_result["verified"] else "unverified"
            error_log = verification_result.get("error")

            # 3. Retry ONCE if verification failed
            if not verification_result["verified"]:
                retry_fixed_code, retry_diff_patch = retry_fix_with_error(
                    finding,
                    file_content,
                    fixed_code,
                    error_log or ""
                )
                retry_verification = verify_fix_in_sandbox(
                    target_filename,
                    retry_fixed_code,
                    finding,
                    repo_files
                )
                if retry_verification["verified"]:
                    status = "verified"
                    fixed_code = retry_fixed_code
                    diff_patch = retry_diff_patch
                    error_log = "Verified on retry #1"
                else:
                    status = "unverified"
                    error_log = f"Retry #1 failed: {retry_verification.get('error')}"

            fixes.append({
                "id": f"FIX-{finding['id']}",
                "finding_id": finding["id"],
                "file": target_filename,
                "category": finding.get("category", ""),
                "severity": finding.get("severity", "high"),
                "diff": diff_patch,
                "status": status,  # "verified" | "unverified"
                "verification_log": error_log or "Syntax compiled clean, scanner issue resolved, tests passed in isolated sandbox.",
                "original_code": file_content,
                "fixed_code": fixed_code
            })

        return fixes

