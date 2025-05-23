"""Simple text analysis utility."""

from collections import Counter
import re


def analyze_text(text: str) -> str:
    """Analyze the given text and return a short summary."""
    words = re.findall(r"\w+", text.lower())
    word_count = len(words)
    most_common = Counter(words).most_common(5)
    common_str = ", ".join(f"{w}({c})" for w, c in most_common)
    return f"{word_count} words. Top terms: {common_str}" if words else "No text provided."
