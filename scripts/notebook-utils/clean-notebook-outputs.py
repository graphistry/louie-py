#!/usr/bin/env python3
"""Clean sensitive outputs from executed notebooks."""

import json
import re
import sys
from pathlib import Path


def clean_notebook_outputs(notebook_path, dry_run=False):
    """Remove outputs containing potential secrets.

    Args:
        notebook_path: Path to the notebook file
        dry_run: If True, only report what would be cleaned without modifying

    Returns:
        tuple: (cleaned_count, total_outputs_count)
    """

    with open(notebook_path) as f:
        nb = json.load(f)

    secret_patterns = [
        r'personal_key_id\s*=\s*["\'](?!your_key_id)[^"\']+["\']',
        r'personal_key_secret\s*=\s*["\'](?!your_key_secret)[^"\']+["\']',
        r'PERSONAL_KEY_ID\s*=\s*["\'](?!your_key_id)[^"\']+["\']',
        r'PERSONAL_KEY_SECRET\s*=\s*["\'](?!your_key_secret)[^"\']+["\']',
        r"pk_[a-zA-Z0-9]+",
        r"sk_[a-zA-Z0-9]+",
        r"FILL_ME_IN",
        r'password\s*=\s*["\'](?!your_password)[^"\']+["\']',
        r'api_key\s*=\s*["\'](?!your_api_key)[^"\']+["\']',
        r'api_secret\s*=\s*["\'](?!your_api_secret)[^"\']+["\']',
        r"getpass\.getpass",
    ]

    cleaned_count = 0
    total_outputs = 0

    for i, cell in enumerate(nb.get("cells", []), 1):
        if cell.get("cell_type") == "code":
            original_outputs = cell.get("outputs", [])
            clean_outputs = []

            for output in original_outputs:
                total_outputs += 1

                # Convert output to string for pattern matching
                if output.get("output_type") == "stream":
                    output_str = "".join(output.get("text", []))
                elif output.get("output_type") == "execute_result":
                    output_str = str(output.get("data", {}))
                elif output.get("output_type") == "error":
                    output_str = "\n".join(output.get("traceback", []))
                else:
                    output_str = json.dumps(output)

                has_secret = any(
                    re.search(pattern, output_str, re.IGNORECASE)
                    for pattern in secret_patterns
                )

                if not has_secret:
                    clean_outputs.append(output)
                else:
                    cleaned_count += 1
                    if dry_run:
                        print(
                            f"Would clean: Cell {i}, output containing sensitive data"
                        )

            if not dry_run:
                cell["outputs"] = clean_outputs

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
