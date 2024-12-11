# Composite Readability Analyzer

This repository provides a Python script to analyze the readability of Markdown files within a Git repository. The script calculates composite readability scores for files across their commit histories and for staged changes. It is inspired by and builds upon the Lexi project by the team at [Rebilly](https://github.com/Rebilly/lexi).

## Features

- **Analyze Specific Files**: Compute readability scores for a specific Markdown file across its commit history.
- **Analyze All Files**: Compute scores for all Markdown files in the repository.
- **Composite Readability Score**: Combines multiple readability metrics for a comprehensive analysis.
- **Output Options**: Results can be displayed as Markdown tables or saved to CSV/XLSX files.
- **Inspired by Lexi**: Acknowledges the readability approach introduced by [Lexi](https://github.com/Rebilly/lexi).

## Installation

Ensure you have Python 3.7 or later installed.

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Analyze a Specific File

To compute readability scores for a specific Markdown file:
```bash
python composite_readability.py -f <file-path>
```

### Analyze All Markdown Files

To compute scores for all Markdown files in the repository:
```bash
python composite_readability.py -a
```

### Save Results to a File

To save results in a CSV or XLSX file:
```bash
python composite_readability.py -a -o results.csv
```

## Metrics Used

The composite readability score combines the following metrics:

- **Flesch Reading Ease**
- **Gunning Fog Index**
- **Coleman-Liau Index**
- **Automated Readability Index**
- **Dale-Chall Readability Score**

Each metric is normalized and weighted to compute a comprehensive readability score.

## Examples

### Command Output

#### Specific File Analysis
```
## Readability history for file: README.md
| Commit                             | Date                | Score |
|------------------------------------|---------------------|-------|
| abc123                             | 2024-12-10T10:00:00 | 85.23 |
| def456                             | 2024-12-11T10:00:00 | 87.45 |
| STAGED                             | 2024-12-11T11:00:00 | 90.12 |
```

#### All Files Analysis
```
## Readability history for file: file1.md
| Commit                             | Date                | Score |
|------------------------------------|---------------------|-------|
| abc123                             | 2024-12-10T10:00:00 | 80.00 |
| def456                             | 2024-12-11T10:00:00 | 82.45 |

## Readability history for file: file2.md
| Commit                             | Date                | Score |
|------------------------------------|---------------------|-------|
| abc123                             | 2024-12-09T10:00:00 | 70.50 |
| def456                             | 2024-12-10T10:00:00 | 73.20 |
```

## Acknowledgments

This project draws inspiration from [Lexi](https://github.com/Rebilly/lexi), developed by the talented team at Rebilly. Lexi introduced the concept of tracking readability improvements for documentation files in pull requests.

