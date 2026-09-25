from typing import List, Dict, Any
from scanners.secret_scanner import scan_file_for_secrets
from scanners.security_scanner import scan_file_for_security_issues
from llm import explain_finding

class SecuritySentinelAgent:
    """Agent 1: Security Sentinel - Detects hardcoded secrets, SQLi, CMDi, credentials."""
    
    def run(self, repo_files: Dict[str, str]) -> List[Dict[str, Any]]:
        findings = []
        for filename, content in repo_files.items():
            if filename.endswith(".py"):
                # Run deterministic scanners
                secret_issues = scan_file_for_secrets(filename, content)
                security_issues = scan_file_for_security_issues(filename, content)
                
                combined = secret_issues + security_issues
                for issue in combined:
                    # Enrich with LLM plain language explanation
                    issue["explanation"] = explain_finding(issue, content)
                    findings.append(issue)
                    
        return findings
