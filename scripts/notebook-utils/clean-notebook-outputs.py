#!/usr/bin/env python3
"""Clean sensitive outputs from executed notebooks."""

import json
import re
import sys
from pathlib import Path


def redact_string(text, patterns_to_redact):
    """Redact sensitive patterns in a string with ****."""
    redacted = text
    for pattern, replacement in patterns_to_redact:
        redacted = re.sub(pattern, replacement, redacted)
    return redacted


def clean_notebook_outputs(notebook_path, dry_run=False):
    """Redact sensitive data in outputs instead of removing entire outputs.

    Args:
        notebook_path: Path to the notebook file
        dry_run: If True, only report what would be cleaned without modifying

    Returns:
        tuple: (cleaned_count, total_outputs_count)
    """

    with open(notebook_path) as f:
        nb = json.load(f)

    # Patterns to search for and their replacements
    secret_patterns = [
        # API keys and secrets - completely redact
        (
            r'personal_key_id\s*=\s*["\'](?!your_key_id)[^"\']+["\']',
            'personal_key_id="****"',
        ),
        (
            r'personal_key_secret\s*=\s*["\'](?!your_key_secret)[^"\']+["\']',
            'personal_key_secret="****"',
        ),
        (
            r'PERSONAL_KEY_ID\s*=\s*["\'](?!your_key_id)[^"\']+["\']',
            'PERSONAL_KEY_ID="****"',
        ),
        (
            r'PERSONAL_KEY_SECRET\s*=\s*["\'](?!your_key_secret)[^"\']+["\']',
            'PERSONAL_KEY_SECRET="****"',
        ),
        (r"pk_[a-zA-Z0-9]+", "pk_****"),
        (r"sk_[a-zA-Z0-9]+", "sk_****"),
        (r"FILL_ME_IN", "****"),
        (r'password\s*=\s*["\'](?!your_password)[^"\']+["\']', 'password="****"'),
        (r'api_key\s*=\s*["\'](?!your_api_key)[^"\']+["\']', 'api_key="****"'),
        (r'api_secret\s*=\s*["\'](?!your_api_secret)[^"\']+["\']', 'api_secret="****"'),
        # Development environment details - replace with generic
        (r"databricks-pat-botsv3", "example-org"),
        (r"graphistry-dev\.grph\.xyz", "hub.graphistry.com"),
        (r"louie-dev\.grph\.xyz", "louie.graphistry.com"),
    ]

    cleaned_count = 0
    total_outputs = 0

    for i, cell in enumerate(nb.get("cells", []), 1):
        if cell.get("cell_type") == "code":
            outputs = cell.get("outputs", [])

            for output in outputs:
                total_outputs += 1
                output_modified = False

                # Handle different output types
                if output.get("output_type") == "stream":
                    # Redact text in stream outputs
                    texts = output.get("text", [])
                    if texts:
                        new_texts = []
                        for text in texts:
                            new_text = redact_string(text, secret_patterns)
                            if new_text != text:
                                output_modified = True
                            new_texts.append(new_text)
                        if not dry_run:
                            output["text"] = new_texts

                elif output.get("output_type") in ["execute_result", "display_data"]:
                    # Redact in execute_result and display_data
                    data = output.get("data", {})
                    if "text/html" in data:
                        html_list = data["text/html"]
                        new_html_list = []
                        for html in html_list:
                            new_html = redact_string(html, secret_patterns)
                            if new_html != html:
                                output_modified = True
                            new_html_list.append(new_html)
                        if not dry_run:
                            data["text/html"] = new_html_list

                    if "text/plain" in data:
                        plain_list = data["text/plain"]
                        new_plain_list = []
                        for plain in plain_list:
                            new_plain = redact_string(plain, secret_patterns)
                            if new_plain != plain:
                                output_modified = True
                            new_plain_list.append(new_plain)
                        if not dry_run:
                            data["text/plain"] = new_plain_list

                elif output.get("output_type") == "error":
                    # Redact in error tracebacks
                    traceback = output.get("traceback", [])
                    if traceback:
                        new_traceback = []
                        for line in traceback:
                            new_line = redact_string(line, secret_patterns)
                            if new_line != line:
                                output_modified = True
                            new_traceback.append(new_line)
                        if not dry_run:
                            output["traceback"] = new_traceback

                if output_modified:
                    cleaned_count += 1
                    if dry_run:
                        print(f"Would redact: Cell {i}, output with sensitive data")

    # Save back if not dry run
    if not dry_run and cleaned_count > 0:
        # Pretty print with minimal indentation for smaller file size
        with open(notebook_path, "w") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)

    return cleaned_count, total_outputs


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean sensitive outputs from Jupyter notebooks"
    )
    parser.add_argument("notebook", help="Path to the notebook file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cleaned without modifying the file",
    )

    args = parser.parse_args()

    notebook_path = Path(args.notebook)

    if not notebook_path.exists():
        print(f"❌ Notebook not found: {notebook_path}")
        sys.exit(1)

    cleaned, total = clean_notebook_outputs(notebook_path, dry_run=args.dry_run)

    if args.dry_run:
        if cleaned > 0:
            print(f"Would clean {cleaned}/{total} outputs containing sensitive data")
        else:
            print("✅ No sensitive outputs found")
    else:
        if cleaned > 0:
            print(f"✅ Cleaned {cleaned}/{total} sensitive outputs from notebook")
        else:
            print("✅ No sensitive outputs found")


if __name__ == "__main__":
    main()
