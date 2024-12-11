from bs4 import BeautifulSoup
from markdown import markdown
import re
import textstat
import pandas as pd
from sys import argv



'''
# Convert Markdown to plain text
def markdown_to_text(markdown_string):
    """ Converts a markdown string to plaintext """
    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # Remove code snippets
    html = re.sub(r'<pre>(.*?)</pre>', ' ', html, flags=re.DOTALL)
    html = re.sub(r'<code>(.*?)</code>', ' ', html, flags=re.DOTALL)

    # Extract text
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))

    return text
'''

def markdown_to_text(markdown_string):
    """
    Processes markdown input to remove unwanted structures and convert it to plain text.
    This mirrors the behavior of the TypeScript preprocessMarkdown function.
    """
    # Step 1: Convert markdown to HTML
    html = markdown(markdown_string)

    # Step 2: Preprocess the HTML
    # Remove tables (convert them to text)
    html = re.sub(r'<table.*?>.*?</table>', '', html, flags=re.DOTALL)

    # Remove URLs within backticks
    html = re.sub(r'`[^`]*https?://\S+[^`]*`', '', html)

    # Remove admonition headings (e.g., "Note:" or "Tip:")
    html = re.sub(r'<blockquote>.*?</blockquote>', '', html, flags=re.DOTALL)

    # Replace colons with periods
    html = html.replace(':', '.')

    # Remove short list items (e.g., items with less than 3 characters)
    html = re.sub(r'<li>\s*[^\s]{1,2}\s*</li>', '', html)

    # Add periods to list items if they don't already have a sentence end
    html = re.sub(r'(<li>.*?)(?<![.?!])\s*</li>', r'\1.</li>', html)

    # Remove JavaScript items (e.g., script tags or inline JavaScript)
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL)

    # Remove unwanted node types like horizontal rules (<hr>)
    html = re.sub(r'<hr.*?>', '', html)

    # Remove image alt text
    html = re.sub(r'<img.*?alt=".*?".*?>', '', html)

    # Remove frontmatter (e.g., YAML frontmatter or other metadata blocks)
    html = re.sub(r'^---[\s\S]*?---', '', html, flags=re.MULTILINE)

    # Step 3: Extract text from HTML
    soup = BeautifulSoup(html, "html.parser")
    text = ''.join(soup.findAll(text=True))

    # Step 4: Final Text Processing
    # Remove any Markdoc tags
    text = re.sub(r'{%[\s\S]*?%}', '', text)

    # Remove blank lines
    text = re.sub(r'\n+', '\n', text)

    # Remove manual word wrapping (newlines preceded by an alphabetical character)
    text = re.sub(r'([a-zA-Z])\n', r'\1 ', text)

    return text

# Define weights, min, max values for readability scores
readability_metrics = {
    "flesch_reading_ease": {"weight": 0.1653977378, "min": 0, "max": 100},
    #"smog_index": {"weight": 0.2, "min": 19, "max": 6},
    "gunning_fog": {"weight": 0.2228367277, "min": 19, "max": 6},
    #"flesch_kincaid_grade": {"weight": 0.2, "min": 0, "max": 25},
    "coleman_liau_index": {"weight": 0.1831723411, "min": 19, "max": 6},
    "automated_readability_index": {"weight": 0.2325290236, "min": 22, "max": 6},
    "dale_chall_readability_score": {"weight": 0.1960641698, "min": 11, "max": 4.9},
}

# Normalization formula
def normalize_score(score, min_val, max_val):
    """ Normalizes the score to a range of 0-1 """
    return (score - min_val) / (max_val - min_val)

# Readability calculation and composite score
def calculate_readability(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # Convert Markdown to plain text
    text = markdown_to_text(markdown_content)

    # Calculate readability scores
    scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        #"smog_index": textstat.smog_index(text),
        #"flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "gunning_fog": textstat.gunning_fog(text),
        "coleman_liau_index": textstat.coleman_liau_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "dale_chall_readability_score": textstat.dale_chall_readability_score(text),
    }

    # Create a DataFrame for the metrics, weights, and scores
    metrics = []
    weighted_normalized_score_sum = 0
    for metric, values in readability_metrics.items():
        weight = values["weight"]
        min_val = values["min"]
        max_val = values["max"]
        score = scores.get(metric, 0)

        # Normalize the score
        normalized_score = normalize_score(score, min_val, max_val)

        # Calculate weighted contribution
        weighted_normalized_score = weight * normalized_score
        weighted_normalized_score_sum += weighted_normalized_score

        metrics.append({
            "Metric": metric,
            "Score": score,
            "Weight": weight,
            "Min": min_val,
            "Max": max_val,
            "Normalized Score": normalized_score,
            "Weighted Normalized Score": weighted_normalized_score,
        })

    # Calculate composite score
    composite_score = weighted_normalized_score_sum * 100

    # Output DataFrame and composite score
    df = pd.DataFrame(metrics)
    return df, composite_score

# Example usage
if __name__ == "__main__":
    if len(argv) < 2:
        print("No files provided for readability check.")
        sys.exit(0)

    for file_path in argv[1:]:
        print(f"\nProcessing file: {file_path}")
        df, composite_score = calculate_readability(file_path)

        print(df)
        print(f"\nComposite Score for {file_path}: {composite_score}")

