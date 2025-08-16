#!/usr/bin/env python3
"""Validate that a version tag is PEP 440 compliant."""

import sys

from packaging.version import InvalidVersion, Version


def validate_tag(tag_name: str) -> bool:
    """
    Validate that a tag name is PEP 440 compliant.

    Args:
        tag_name: The tag name to validate (e.g., 'v0.6.0', '0.6.0a1')

    Returns:
        True if valid, False otherwise
    """
    # Remove 'v' prefix if present
    version = tag_name.lstrip("v")

    try:
        Version(version)
        return True
    except InvalidVersion:
        return False


def print_valid_formats():
    """Print examples of valid version formats."""
    print("\n✅ Valid version formats (PEP 440):")
    print("  - v0.6.0          (release)")
    print("  - v0.6.0a1        (alpha release)")
    print("  - v0.6.0b1        (beta release)")
    print("  - v0.6.0rc1       (release candidate)")
    print("  - v0.6.0.dev1     (development release)")
    print("  - v0.6.0.post1    (post-release)")
    print("  - v0.6.1a1.dev1   (dev release of alpha)")

    print("\n❌ Invalid formats:")
    print("  - v0.6.0-preview  (use v0.6.0a1 instead)")
    print("  - v0.6.0-feature  (use v0.6.0.dev1 instead)")
    print("  - v0.6.0-beta     (use v0.6.0b1 instead)")
    print("  - v0.6.0-rc       (use v0.6.0rc1 instead)")


def main():
    """Main function to validate tag from command line."""
    if len(sys.argv) != 2:
        print("Usage: python validate-version-tag.py <tag_name>")
        print_valid_formats()
        sys.exit(1)

    tag_name = sys.argv[1]

    if validate_tag(tag_name):
        print(f"✅ Tag '{tag_name}' is PEP 440 compliant")
        sys.exit(0)
    else:
        print(f"❌ Tag '{tag_name}' is NOT PEP 440 compliant")
        print_valid_formats()
        sys.exit(1)


if __name__ == "__main__":
    main()
