import ast
import re
from typing import List, Dict, Any

class SecurityASTVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, lines: List[str]):
        self.filename = filename
        self.lines = lines
        self.findings = []

    def visit_Assign(self, node):
        # Catch query = f"SELECT ..." or query = "SELECT ... %s" % var or query = "SELECT {}".format(var)
        if isinstance(node.value, (ast.JoinedStr, ast.BinOp, ast.Call)):
            line_no = node.lineno
            line_text = self.lines[line_no - 1].strip() if line_no <= len(self.lines) else ""
            if "SELECT" in line_text and ("WHERE" in line_text or "FROM" in line_text):
                is_unsafe = False
                if isinstance(node.value, ast.JoinedStr):
                    is_unsafe = True
                elif isinstance(node.value, ast.BinOp) and isinstance(node.value.op, (ast.Mod, ast.Add)):
                    is_unsafe = True
                elif isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "format":
                    is_unsafe = True

                if is_unsafe:
                    self.findings.append({
                        "id": f"SEC-SQLI-{self.filename}-{line_no}",
                        "type": "security",
                        "category": "SQL Injection",
                        "severity": "high",
                        "file": self.filename,
                        "line": line_no,
                        "description": "SQL query built dynamically using string formatting/concatenation. Exposes database to SQL Injection (CWE-89).",
                        "code_snippet": line_text,
                        "cwe": "CWE-89: Improper Neutralization of Special Elements used in an SQL Command"
                    })
        self.generic_visit(node)

    def visit_Call(self, node):
        # Catch cursor.execute(query) or cursor.execute(f"SELECT ...")
        if isinstance(node.func, ast.Attribute) and node.func.attr == "execute":
            line_no = node.lineno
            line_text = self.lines[line_no - 1].strip() if line_no <= len(self.lines) else ""
            
            # Check if arg is f-string or single variable (like query) derived from unsafe string formatting
            if node.args:
                arg0 = node.args[0]
                is_unsafe = False
                if isinstance(arg0, ast.JoinedStr):
                    is_unsafe = True
                elif isinstance(arg0, ast.BinOp) and isinstance(arg0.op, (ast.Mod, ast.Add)):
                    is_unsafe = True
                elif isinstance(arg0, ast.Call) and isinstance(arg0.func, ast.Attribute) and arg0.func.attr == "format":
                    is_unsafe = True
                
                if is_unsafe and not any(f["line"] == line_no and f["category"] == "SQL Injection" for f in self.findings):
                    self.findings.append({
                        "id": f"SEC-SQLI-EXEC-{self.filename}-{line_no}",
                        "type": "security",
                        "category": "SQL Injection",
                        "severity": "high",
                        "file": self.filename,
                        "line": line_no,
                        "description": "Unsafe string formatting passed directly to database execute(). Exposes database to SQL Injection (CWE-89).",
                        "code_snippet": line_text,
                        "cwe": "CWE-89: Improper Neutralization of Special Elements used in an SQL Command"
                    })

        # Catch os.system / subprocess.Popen with shell=True
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["system", "popen"] and getattr(node.func.value, "id", "") == "os":
                line_no = node.lineno
                self.findings.append({
                    "id": f"SEC-CMDI-{self.filename}-{line_no}",
                    "type": "security",
                    "category": "Command Injection",
                    "severity": "critical",
                    "file": self.filename,
                    "line": line_no,
                    "description": "Execution of system command via os.system(). Unsanitized input leads to Command Execution.",
                    "code_snippet": self.lines[line_no - 1].strip() if line_no <= len(self.lines) else "",
                    "cwe": "CWE-78: Improper Neutralization of Special Elements used in an OS Command"
                })

        self.generic_visit(node)

def scan_file_for_security_issues(filename: str, content: str) -> List[Dict[str, Any]]:
    findings = []
    lines = content.splitlines()

    try:
        tree = ast.parse(content, filename=filename)
        visitor = SecurityASTVisitor(filename, lines)
        visitor.visit(tree)
        findings.extend(visitor.findings)
    except SyntaxError:
        pass

    # Regex Fallback for SQL Injection patterns
    sql_regex = r"(?i)(SELECT.*WHERE.*=.*['\"]?\s*\{|execute\s*\(\s*f['\"]SELECT)"
    for idx, line in enumerate(lines, 1):
        if re.search(sql_regex, line):
            if not any(f["line"] == idx and f["category"] == "SQL Injection" for f in findings):
                findings.append({
                    "id": f"SEC-SQLI-REGEX-{filename}-{idx}",
                    "type": "security",
                    "category": "SQL Injection",
                    "severity": "high",
                    "file": filename,
                    "line": idx,
                    "description": "SQL query built dynamically using f-string or string formatting. Exposes database to SQL Injection.",
                    "code_snippet": line.strip(),
                    "cwe": "CWE-89: Improper Neutralization of Special Elements used in an SQL Command"
                })

    return findings
