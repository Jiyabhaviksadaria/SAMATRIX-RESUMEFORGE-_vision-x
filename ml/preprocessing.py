import re
import pandas as pd
from typing import List, Tuple, Optional

# Basic English stopwords list to prevent mandatory heavy NLTK download overhead
BASIC_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't",
    "down", "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him",
    "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't",
    "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor",
    "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out",
    "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so",
    "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which", "while",
    "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves"
}


def remove_urls(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r'https?://\S+|www\.\S+', ' ', text)


def remove_emails(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' ', text)


def remove_phone_numbers(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return re.sub(r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}', ' ', text)


def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = remove_urls(text)
    text = remove_emails(text)
    text = remove_phone_numbers(text)
    # Remove special punctuation while keeping technical symbols like C++, .NET
    text = re.sub(r'[^a-zA-Z0-9\+#\s\.]', ' ', text)
    # Replace multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()


def clean_text(text: str, remove_stopwords: bool = False) -> str:
    normalized = normalize_text(text)
    if not remove_stopwords:
        return normalized

    tokens = normalized.split()
    filtered = [t for t in tokens if t not in BASIC_STOPWORDS and len(t) > 1]
    return " ".join(filtered)


def combine_text_columns(df: pd.DataFrame, text_cols: List[str]) -> pd.Series:
    if not text_cols:
        # Fallback to all object columns
        text_cols = [c for c in df.columns if df[c].dtype == 'object']
    if not text_cols:
        raise ValueError("No text columns found to combine.")

    combined = df[text_cols[0]].fillna("").astype(str)
    for col in text_cols[1:]:
        combined = combined + " " + df[col].fillna("").astype(str)
    return combined


def prepare_text_dataset(df: pd.DataFrame, text_cols: List[str]) -> Tuple[pd.Series, pd.Series]:
    raw_text_series = combine_text_columns(df, text_cols)
    clean_text_series = raw_text_series.apply(clean_text)
    return raw_text_series, clean_text_series
