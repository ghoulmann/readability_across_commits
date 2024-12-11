#!/usr/bin/env python3

import subprocess
import sys
import re
import argparse
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from markdown import markdown
import textstat
import pandas as pd
from datetime import datetime
import pytz
import dateutil.parser

def run_git_command(command: List[str]) -> str:
    """Run a git command and return its output."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: Unable to run git command: {' '.join(command)}", file=sys.stderr)
        sys.exit(1)

def get_commit_history(file_path: Optional[str] = None) -> List[str]:
    """Retrieve commit hashes for a specific file or all files."""
    command = ["git", "log", "--format=%H|%cd", "--date=iso-local"]
    if file_path:
        command.append(file_path)
    return run_git_command(command).splitlines()

def get_file_content_at_commit(commit_hash: str, file_path: str) -> str:
    """Retrieve the file content at a specific commit."""
    try:
        return run_git_command(["git", "show", f"{commit_hash}:{file_path}"])
    except subprocess.CalledProcessError:
        print(f"Warning: Unable to retrieve content for {file_path} at commit {commit_hash}", file=sys.stderr)
        return ""

def markdown_to_text(markdown_string: str) -> str:
    """
    Processes markdown input to remove unwanted structures and convert it to plain text.
    """
    # Remove all fenced code blocks (with or without language specifier, indented or not)
    markdown_string = re.sub(
        r"(^|\n)\s*```(?:[^\n]*)?\n[\s\S]*?\n\s*```", 
        "\n", 
        markdown_string, 
        flags=re.MULTILINE
    )

    html = markdown(markdown_string)
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted elements using decompose
    for tag in soup.find_all(["table", "script", "blockquote", "hr", "img", "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6"]):
        tag.decompose()

    # Process <a> tags to extract meaningful text
    for tag in soup.find_all("a"):
        tag.replace_with(tag.get_text())

    text = ''.join(soup.stripped_strings)
    text = re.sub(r'{%[\s\S]*?%}', '', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'([a-zA-Z])\n', r'\1 ', text)
    return text

readability_metrics = {
    "flesch_reading_ease": {"weight": 0.1653977378, "min": 0, "max": 100},
    "gunning_fog": {"weight": 0.2228367277, "min": 19, "max": 6},
    "coleman_liau_index": {"weight": 0.1831723411, "min": 19, "max": 6},
    "automated_readability_index": {"weight": 0.2325290236, "min": 22, "max": 6},
    "dale_chall_readability_score": {"weight": 0.1960641698, "min": 11, "max": 4.9},
}

def normalize_score(score, min_val, max_val):
    """ Normalize the score to a range of 0-1 """
    return (score - min_val) / (max_val - min_val)

def calculate_readability(content: str) -> float:
    """Calculate a composite readability score for the given content."""
    text = markdown_to_text(content)
    scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "gunning_fog": textstat.gunning_fog(text),
        "coleman_liau_index": textstat.coleman_liau_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "dale_chall_readability_score": textstat.dale_chall_readability_score(text),
    }

    weighted_normalized_score_sum = 0
    for metric, values in readability_metrics.items():
        weight = values["weight"]
        min_val = values["min"]
        max_val = values["max"]
        score = scores.get(metric, 0)
        normalized_score = normalize_score(score, min_val, max_val)
        weighted_normalized_score_sum += weight * normalized_score

    composite_score = weighted_normalized_score_sum * 100
    return composite_score

def get_all_markdown_files() -> List[str]:
    """Retrieve all Markdown files in the repository."""
    files = run_git_command(["git", "ls-files", "*.md"]).splitlines()
    return files

def analyze_readability(file_path: str) -> List[Dict[str, str]]:
    """Analyze readability scores across commits for a specific file."""
    results = []
    commits = get_commit_history(file_path)

    for entry in commits:
        commit_hash, commit_date = entry.split('|')
        # Parse and normalize the date
        try:
            commit_date = dateutil.parser.parse(commit_date).astimezone().isoformat()
        except ValueError:
            print(f"Warning: Invalid date format for commit {commit_hash}", file=sys.stderr)
            continue
        content = get_file_content_at_commit(commit_hash, file_path)
        if content:
            score = calculate_readability(content)
            results.append({
                "file": file_path,
                "commit": commit_hash,
                "date": commit_date,
                "score": score
            })

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            staged_content = f.read()
        staged_score = calculate_readability(staged_content)
        results.append({
            "file": file_path,
            "commit": "STAGED",
            "date": datetime.now().astimezone().isoformat(),
            "score": staged_score
        })
    except FileNotFoundError:
        pass

    return results

def analyze_all_files(output_file: Optional[str] = None):
    """Analyze readability history for all Markdown files in the repository."""
    all_files = get_all_markdown_files()
    if not all_files:
        print("No Markdown files found in the repository.")
        return

    all_results = []
    for file_path in all_files:
        print(f"Analyzing {file_path} across commits...")
        results = analyze_readability(file_path)
        all_results.extend(results)

    if output_file:
        output_results(all_results, output_file)
    else:
        display_results(all_results)

def display_results(results: List[Dict[str, str]]):
    """Tabulate and display results to the terminal with markdown tables."""
    grouped_results = {}
    for result in results:
        grouped_results.setdefault(result["file"], []).append(result)

    for file, entries in grouped_results.items():
        print(f"\n## Readability history for file: {file}")
        print("| Commit | Date | Score |")
        print("|--------|------|-------|")
        for entry in entries:
            print(f"| {entry['commit']} | {entry['date']} | {entry['score']:.2f} |")

def output_results(results: List[Dict[str, str]], output_file: str):
    """Write results to an output file in CSV or XLSX format."""
    df = pd.DataFrame(results)
    if output_file.endswith(".xlsx"):
        df.to_excel(output_file, index=False)
    elif output_file.endswith(".csv"):
        df.to_csv(output_file, index=False)
    print(f"Results written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Analyze composite readability scores for Markdown files.")
    parser.add_argument("-f", "--file", help="Specify a Markdown file to analyze.")
    parser.add_argument("-a", "--all", action="store_true", help="Analyze all Markdown files across commits.")
    parser.add_argument("-o", "--output", help="Specify an output file (CSV or XLSX) to save results.")

    args = parser.parse_args()

    if not args.file and not args.all:
        print("Error: You must specify either a file with -f or use -a to analyze all Markdown files.", file=sys.stderr)
        sys.exit(1)

    if args.all:
        analyze_all_files(args.output)
    else:
        if args.file:
            results = analyze_readability(args.file)
            if args.output:
                output_results(results, args.output)
            else:
                display_results(results)

if __name__ == "__main__":
    main()
