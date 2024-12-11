#!/usr/bin/env python3

import subprocess
import sys
from typing import List
from commit_readability_history import calculate_readability, markdown_to_text

def get_staged_files(extension: str) -> List[str]:
    """Retrieve all staged files with the specified extension."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        files = result.stdout.splitlines()
        return [f for f in files if f.endswith(extension)]
    except subprocess.CalledProcessError:
        print("Error: Unable to get staged files.", file=sys.stderr)
        sys.exit(1)

def main():
    # Set a readability threshold
    THRESHOLD = 50.0

    # Get all staged Markdown files
    markdown_files = get_staged_files(".md")

    if not markdown_files:
        print("No staged Markdown files to check.")
        sys.exit(0)

    failed = False

    for file_path in markdown_files:
        print(f"Checking readability for: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            readability_score = calculate_readability(content)
            print(f"  Readability Score: {readability_score:.2f}")
            
            if readability_score < THRESHOLD:
                print(f"  [ERROR] Readability score below threshold ({THRESHOLD}): {readability_score:.2f}")
                failed = True
        except FileNotFoundError:
            print(f"  [ERROR] File {file_path} not found.")
            sys.exit(1)

    if failed:
        print("Pre-commit check failed. Fix the issues and try again.")
        sys.exit(1)

    print("Readability check passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
