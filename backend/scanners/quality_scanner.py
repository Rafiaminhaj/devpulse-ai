import ast
import os
from typing import List, Dict, Any

def is_test_file(filepath: str) -> bool:
    """Checks if a file path is a test file (e.g. test_*.py, *_test.py, or inside test/ / tests/ directory)."""
    norm_path = filepath.replace("\\", "/").lower()
    parts = norm_path.split("/")
    basename = parts[-1]

    if basename.startswith("test_") or basename.endswith("_test.py"):
        return True

    if any(part in ("test", "tests") for part in parts[:-1]):
        return True

    return False

class QualityASTVisitor(ast.NodeVisitor):
    def __init__(self, filename: str, lines: List[str]):
        self.filename = filename
        self.lines = lines
        self.findings = []
        self.function_complexities = {}

    def visit_FunctionDef(self, node):
        # Calculate Cyclomatic Complexity (count if/elif/for/while/try/except/and/or)
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        if complexity > 7:
            severity = "high" if complexity > 12 else "medium"
            self.findings.append({
                "id": f"QUAL-COMPLEX-{self.filename}-{node.lineno}",
                "type": "quality",
                "category": "High Cyclomatic Complexity",
                "severity": severity,
                "file": self.filename,
                "line": node.lineno,
                "description": f"Function '{node.name}' has cyclomatic complexity of {complexity} (threshold: 7). High complexity makes code hard to test and maintain.",
                "code_snippet": f"def {node.name}(...):",
                "cwe": "CWE-1074: Class or Function with Excessive Cyclomatic Complexity",
                "auto_fixable": False,
                "manual_review_note": "Manual review recommended: Decomposing complex function branching requires human architectural redesign."
            })

        self.generic_visit(node)

    def visit_Call(self, node):
        # Resource Leak / Missing Error Handling: Unhandled open(...) without 'with' statement
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            line_no = node.lineno
            line_text = self.lines[line_no - 1].strip() if line_no <= len(self.lines) else ""
            if not line_text.startswith("with open"):
                self.findings.append({
                    "id": f"QUAL-RESOURCE-{self.filename}-{line_no}",
                    "type": "quality",
                    "category": "Resource Leak & Missing Error Handling",
                    "severity": "medium",
                    "file": self.filename,
                    "line": line_no,
                    "description": "File opened directly without context manager ('with' statement) or try-finally block. Can cause unclosed file descriptor leak and unhandled FileNotFoundError.",
                    "code_snippet": line_text,
                    "cwe": "CWE-775: Missing Release of File Descriptor or Resource",
                    "auto_fixable": True
                })

        self.generic_visit(node)

def scan_file_for_quality_issues(filename: str, content: str, all_files: List[str] = None) -> List[Dict[str, Any]]:
    findings = []
    lines = content.splitlines()

    try:
        tree = ast.parse(content, filename=filename)
        visitor = QualityASTVisitor(filename, lines)
        visitor.visit(tree)
        findings.extend(visitor.findings)
    except SyntaxError:
        pass

    # Check for test coverage / presence (EXCLUDE test files themselves)
    if all_files is not None and not is_test_file(filename):
        has_test = any(is_test_file(f) for f in all_files)
        if not has_test:
            # Flag missing test suite at repo level once
            findings.append({
                "id": f"QUAL-NOTEST-{filename}-1",
                "type": "quality",
                "category": "Missing Test Coverage",
                "severity": "low",
                "file": filename,
                "line": 1,
                "description": "No corresponding test file (test_*.py or test/ directory) detected in repository for modified Python modules.",
                "code_snippet": filename,
                "cwe": "CWE-1077: Floating Test Failure / Insufficient Test Suite",
                "auto_fixable": False,
                "manual_review_note": "Manual review recommended: Test suite creation requires project-level test framework setup."
            })

    return findings

