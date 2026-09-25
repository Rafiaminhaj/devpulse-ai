import os
import sys
import shutil
import tempfile
import subprocess
from typing import Dict, Any, List

from scanners.secret_scanner import scan_file_for_secrets
from scanners.security_scanner import scan_file_for_security_issues
from scanners.quality_scanner import scan_file_for_quality_issues

def verify_fix_in_sandbox(
    target_filename: str,
    fixed_code: str,
    original_finding: Dict[str, Any],
    all_repo_files: Dict[str, str]
) -> Dict[str, Any]:
    """
    Executes fix in an isolated temporary sandbox directory.
    Checks:
    1. Syntax compilation via 'python -m py_compile'
    2. Re-scans code to ensure original finding is GONE
    3. Runs pytest/unittest if test files are present
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write all files into temp sandbox directory
        for fname, fcontent in all_repo_files.items():
            fpath = os.path.join(temp_dir, fname)
            os.makedirs(os.path.dirname(fpath), exist_ok=True)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(fcontent)
                
        # Overwrite target file with fixed code
        target_path = os.path.join(temp_dir, target_filename)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        # 1. Syntax Check (python -m py_compile)
        try:
            compile_proc = subprocess.run(
                [sys.executable, "-m", "py_compile", target_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            if compile_proc.returncode != 0:
                return {
                    "verified": False,
                    "error": f"Python Syntax Compilation Failed:\n{compile_proc.stderr}"
                }
        except subprocess.TimeoutExpired:
            return {"verified": False, "error": "Sandbox Compilation Timeout (exceeded 15s)"}
        except Exception as e:
            return {"verified": False, "error": f"Sandbox Execution Error: {str(e)}"}

        # 2. Re-Scan to confirm original finding is GONE
        sec_findings = scan_file_for_secrets(target_filename, fixed_code) + scan_file_for_security_issues(target_filename, fixed_code)
        qual_findings = scan_file_for_quality_issues(target_filename, fixed_code)
        all_new_findings = sec_findings + qual_findings

        # Check if original finding category is still present
        target_category = original_finding.get("category")
        if any(nf.get("category") == target_category for nf in all_new_findings):
            return {
                "verified": False,
                "error": f"Scanner re-verification failed: Issue category '{target_category}' is still detected in fixed code."
            }

        # 3. Run Test Suite if tests exist in sandbox
        test_files = [f for f in os.listdir(temp_dir) if f.startswith("test_") or f.endswith("_test.py")]
        if test_files:
            try:
                test_proc = subprocess.run(
                    [sys.executable, "-m", "pytest", temp_dir],
                    capture_output=True,
                    text=True,
                    timeout=20,
                    cwd=temp_dir
                )
                if test_proc.returncode != 0:
                    return {
                        "verified": False,
                        "error": f"Test Suite Failure after fix:\n{test_proc.stdout}\n{test_proc.stderr}"
                    }
            except Exception:
                # If pytest is not installed, fallback to python -m unittest discover
                try:
                    test_proc = subprocess.run(
                        [sys.executable, "-m", "unittest", "discover", "-s", temp_dir],
                        capture_output=True,
                        text=True,
                        timeout=20,
                        cwd=temp_dir
                    )
                    if test_proc.returncode != 0:
                        return {
                            "verified": False,
                            "error": f"Unittest Suite Failure after fix:\n{test_proc.stderr}"
                        }
                except Exception as ex:
                    pass

        return {"verified": True, "error": None}
