import time
from typing import Dict, Any, List, Generator

from agents.security_sentinel import SecuritySentinelAgent
from agents.quality_architecture import QualityArchitectureAgent
from agents.auto_fix_agent import AutoFixAgent
from health_score import calculate_health_score
from integrations.jira_client import process_findings_for_jira

class DevPulsePipeline:
    """Orchestrates the 3-agent pipeline, Jira Auto-Ticket Integration, and progress streaming."""

    def __init__(self):
        self.security_agent = SecuritySentinelAgent()
        self.quality_agent = QualityArchitectureAgent()
        self.auto_fix_agent = AutoFixAgent()

    def run_pipeline(self, repo_files: Dict[str, str], pr_meta: Dict[str, Any] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        # Agent 1: Security Sentinel
        sec_findings = self.security_agent.run(repo_files)
        
        # Agent 2: Quality & Architecture Agent
        qual_findings = self.quality_agent.run(repo_files)
        
        all_findings = sec_findings + qual_findings

        # Optional Feature: Process Critical/High Findings for Jira Auto-Creation
        all_findings = process_findings_for_jira(all_findings)
        
        # Agent 3: Auto-Fix Agent
        fixes = self.auto_fix_agent.run(all_findings, repo_files)
        
        # Compute Health Score
        health = calculate_health_score(all_findings, repo_files)
        
        elapsed_sec = round(time.time() - start_time, 2)
        
        jira_tickets_created = sum(1 for f in all_findings if f.get("jira_ticket_url"))
        
        return {
            "pr": pr_meta or {"title": "Pull Request Analysis", "author": "devpulse", "repo": "demo/vulnerable_app"},
            "health_score": health,
            "summary": {
                "total_findings": len(all_findings),
                "security_count": len(sec_findings),
                "quality_count": len(qual_findings),
                "fixes_generated": len(fixes),
                "verified_fixes": sum(1 for f in fixes if f.get("status") == "verified"),
                "jira_tickets_created": jira_tickets_created,
                "execution_time_sec": elapsed_sec
            },
            "findings": all_findings,
            "fixes": fixes,
            "files_analyzed": list(repo_files.keys())
        }
