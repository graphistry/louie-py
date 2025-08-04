#!/usr/bin/env python3
"""Validate notebook for secrets and proper execution."""

import json
import re
import sys
from pathlib import Path


def check_notebook_for_secrets(notebook_path):
    """Check notebook outputs for leaked secrets."""

    with open(notebook_path) as f:
        nb = json.load(f)

    issues = []
    secret_patterns = [
        r'personal_key_id\s*=\s*["\'](?!your_key_id)[^"\']+["\']',
        r'personal_key_secret\s*=\s*["\'](?!your_key_secret)[^"\']+["\']',
        r"pk_[a-zA-Z0-9]+",
        r"sk_[a-zA-Z0-9]+",
        r"FILL_ME_IN",
        r'password\s*=\s*["\'](?!your_password)[^"\']+["\']',
        r'api_key\s*=\s*["\'](?!your_api_key)[^"\']+["\']',
    ]

    for i, cell in enumerate(nb.get("cells", []), 1):
        if cell.get("cell_type") == "code":
            # Check source for FILL_ME_IN
            source = "".join(cell.get("source", []))
            if "FILL_ME_IN" in source:
                issues.append(f"Cell {i}: Source contains FILL_ME_IN placeholder")

            # Check outputs
            for j, output in enumerate(cell.get("outputs", [])):
                # Convert output to string for pattern matching
                if output.get("output_type") == "stream":
                    output_str = "".join(output.get("text", []))
                elif output.get("output_type") == "execute_result":
                    output_str = str(output.get("data", {}))
                elif output.get("output_type") == "error":
                    output_str = "\n".join(output.get("traceback", []))
                else:
                    output_str = json.dumps(output)

                for pattern in secret_patterns:
                    if re.search(pattern, output_str, re.IGNORECASE):
                        issues.append(
                            f"Cell {i}, Output {j + 1}: Potential secret matching "
                            f"{pattern}"
                        )

    return issues


def check_notebook_executed(notebook_path):
    """Check if notebook has been executed."""

    with open(notebook_path) as f:
        nb = json.load(f)

    executed_cells = 0
    total_code_cells = 0

    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            total_code_cells += 1
            if cell.get("outputs") and len(cell["outputs"]) > 0:
                executed_cells += 1

    return executed_cells, total_code_cells


def check_for_errors(notebook_path):
    """Check for execution errors in notebook."""

    with open(notebook_path) as f:
        nb = json.load(f)

    errors = []

    for i, cell in enumerate(nb.get("cells", []), 1):
        if cell.get("cell_type") == "code":
            for output in cell.get("outputs", []):
                if output.get("output_type") == "error":
                    error_name = output.get("ename", "Unknown")
                    error_value = output.get("evalue", "No message")
                    errors.append(f"Cell {i}: {error_name}: {error_value}")

    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate-notebook.py <notebook.ipynb>")
        sys.exit(1)

    notebook_path = Path(sys.argv[1])

    if not notebook_path.exists():
        print(f"❌ Notebook not found: {notebook_path}")
        sys.exit(1)

    # Check execution
    executed, total = check_notebook_executed(notebook_path)
    if executed == 0:
        print(f"❌ Notebook has not been executed (0/{total} code cells have outputs)")
    elif executed < total:
        print(
            f"⚠️  Notebook partially executed ({executed}/{total} code cells "
            f"have outputs)"
        )
    else:
        print(f"✅ Notebook has been executed ({executed}/{total} code cells)")

    # Check for execution errors
    errors = check_for_errors(notebook_path)
    if errors:
        print("\n❌ Execution errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ No execution errors found")

    # Check for secrets
    issues = check_notebook_for_secrets(notebook_path)

    if issues:
        print("\n❌ Security issues found:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("✅ No secrets found in notebook")
        sys.exit(0)
