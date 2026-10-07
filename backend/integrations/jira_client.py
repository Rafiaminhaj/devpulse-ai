import os
import requests
import logging
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("DevPulseJira")

def create_jira_ticket(finding: dict) -> dict:
    """
    Creates a Jira ticket for Critical or High severity findings.
    Handles errors gracefully without stopping the audit pipeline.
    """
    enabled = os.getenv("JIRA_INTEGRATION_ENABLED", "false").lower() in ("true", "1", "yes")
    if not enabled:
        return {"success": False, "reason": "Jira integration disabled"}

    domain = os.getenv("JIRA_DOMAIN_URL", "").rstrip("/")
    email = os.getenv("JIRA_USER_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    project_key = os.getenv("JIRA_PROJECT_KEY", "")

    if not (domain and email and token and project_key):
        logger.warning("Jira integration enabled but missing credentials in .env")
        return {"success": False, "reason": "Missing Jira credentials"}

    severity = str(finding.get("severity", "Medium")).capitalize()
    if severity not in ["Critical", "High"]:
        return {"success": False, "reason": f"Severity {severity} does not meet Critical/High threshold"}

    # Priority mapping
    priority_map = {
        "Critical": "Highest",
        "High": "High"
    }
    jira_priority = priority_map.get(severity, "High")

    title = finding.get("title", "Code Audit Finding")
    file_name = finding.get("file", "unknown")
    line_num = finding.get("line", 1)
    description_text = finding.get("description", "No description provided.")
    suggested_fix = finding.get("suggested_fix", "")

    summary = f"[DevPulse AI] {severity}: {title} ({file_name}:{line_num})"

    # Construct Atlassian Document Format (ADF) description for Jira v3 API
    adf_description = {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": f"DevPulse AI Audit found a {severity} issue in "},
                    {"type": "text", "text": f"{file_name}", "marks": [{"type": "strong"}]},
                    {"type": "text", "text": f" (Line {line_num})."}
                ]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Description: ", "marks": [{"type": "strong"}]},
                    {"type": "text", "text": description_text}
                ]
            }
        ]
    }

    if suggested_fix:
        adf_description["content"].append({
            "type": "paragraph",
            "content": [{"type": "text", "text": "Suggested Fix / Unified Patch:", "marks": [{"type": "strong"}]}]
        })
        adf_description["content"].append({
            "type": "codeBlock",
            "attrs": {"language": "python"},
            "content": [{"type": "text", "text": suggested_fix}]
        })

    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": adf_description,
            "issuetype": {"name": "Bug"}
        }
    }

    url = f"{domain}/rest/api/3/issue"
    auth = (email, token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, auth=auth, headers=headers, timeout=10)
        
        # Fallback to simple issue creation if priority field fails
        if response.status_code not in (200, 201):
            # Retry without explicit priority if schema rejected it
            payload_simple = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": f"DevPulse AI Audit - {severity}: {title}\nFile: {file_name}:{line_num}\nDescription: {description_text}\nSuggested Fix:\n{suggested_fix}",
                    "issuetype": {"name": "Task"}
                }
            }
            response = requests.post(f"{domain}/rest/api/2/issue", json=payload_simple, auth=auth, headers=headers, timeout=10)

        if response.status_code in (200, 201):
            data = response.json()
            ticket_key = data.get("key")
            ticket_url = f"{domain}/browse/{ticket_key}"
            logger.info(f"Successfully created Jira ticket {ticket_key} at {ticket_url}")
            return {
                "success": True,
                "ticket_key": ticket_key,
                "ticket_url": ticket_url
            }
        else:
            logger.error(f"Jira API error ({response.status_code}): {response.text}")
            return {"success": False, "error": f"Jira HTTP {response.status_code}: {response.text[:200]}"}

    except Exception as e:
        logger.error(f"Failed to connect to Jira API: {str(e)}")
        return {"success": False, "error": str(e)}

def process_findings_for_jira(findings: list) -> list:
    """
    Iterates through findings and attaches Jira ticket URLs to Critical/High severity findings.
    """
    for finding in findings:
        severity = str(finding.get("severity", "Medium")).capitalize()
        if severity in ["Critical", "High"]:
            jira_res = create_jira_ticket(finding)
            if jira_res.get("success"):
                finding["jira_ticket_key"] = jira_res.get("ticket_key")
                finding["jira_ticket_url"] = jira_res.get("ticket_url")
    return findings
