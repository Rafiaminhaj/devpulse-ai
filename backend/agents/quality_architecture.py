from typing import List, Dict, Any
from scanners.quality_scanner import scan_file_for_quality_issues
from llm import explain_finding

class QualityArchitectureAgent:
    """Agent 2: Quality & Architecture Agent - Detects code smells, complexity, unhandled resources, missing tests."""

    def run(self, repo_files: Dict[str, str]) -> List[Dict[str, Any]]:
        findings = []
        all_filenames = list(repo_files.keys())

        for filename, content in repo_files.items():
            if filename.endswith(".py"):
                quality_issues = scan_file_for_quality_issues(filename, content, all_filenames)
                for issue in quality_issues:
                    issue["explanation"] = explain_finding(issue, content)
                    findings.append(issue)

        return findings
