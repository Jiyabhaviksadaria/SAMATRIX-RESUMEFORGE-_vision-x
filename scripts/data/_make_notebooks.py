import json
from pathlib import Path

def md(src): return {"cell_type": "markdown", "metadata": {}, "source": src.strip().splitlines(keepends=True)}
def code(src): return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src.strip().splitlines(keepends=True)}

nb1 = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.13"}},
    "cells": [
        md("# 01 — Resume PDF Extraction\nMember 1 data pipeline: raw PDF resumes → canonical `data/processed/resumes.csv`.\n\nRun notebooks from the repository root (`notebooks/` is auto-detected)."),
        code("""
from pathlib import Path
import sys
ROOT = Path.cwd()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
import pymupdf
print('Root:', ROOT)
"""),
        md("## OCR decision check\nSample 20 PDFs and measure how many contain extractable text."),
        code("""
import random
DATA = ROOT / 'data' / 'raw' / 'resume_dataset' / 'data' / 'data'
pdfs = sorted(DATA.rglob('*.pdf'), key=lambda p: (p.parent.name, p.name))
print('Total PDFs:', len(pdfs))
random.seed(42)
sample = random.sample(pdfs, 20)
ok = 0
for p in sample:
    with pymupdf.open(str(p)) as doc:
        t = ''.join(pg.get_text() for pg in doc)
    if len(t.strip()) > 50:
        ok += 1
print(f'{ok}/20 sampled PDFs had extractable text.')
print('Decision: normal text extraction is sufficient — no OCR pipeline needed.')
"""),
        md("## Run extraction\nProduces `data/processed/resumes.csv`, `reports/eda/extraction_report.json`, and failures CSV when needed."),
        code("""
import subprocess
result = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'data' / 'extract_resumes.py')], cwd=ROOT)
print('exit code:', result.returncode)
"""),
        md("## Inspect the canonical dataset"),
        code("""
import pandas as pd, json
df = pd.read_csv(ROOT / 'data' / 'processed' / 'resumes.csv')
print(df.shape)
print(df.head(3)[['resume_id','filename','category']])
print(df['category'].nunique(), 'categories')
print(json.loads((ROOT / 'reports' / 'eda' / 'extraction_report.json').read_text()))
"""),
    ],
}

nb2 = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                 "language_info": {"name": "python", "version": "3.13"}},
    "cells": [
        md("# 02 — Exploratory Data Analysis\nEDA over `data/processed/resumes.csv`. All artifacts go to `reports/eda/`.\nNo TF-IDF fitting on the full dataset for modeling is exported — class-keyword TF-IDF below is used only for visualization of category-distinguishing terms."),
        code("""
from pathlib import Path
import sys, re
ROOT = Path.cwd()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
EDA = ROOT / 'reports' / 'eda'
EDA.mkdir(parents=True, exist_ok=True)

import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
df = pd.read_csv(ROOT / 'data' / 'processed' / 'resumes.csv')
df['text'] = df['text'].fillna('')
df['word_count'] = df['text'].apply(lambda t: len(t.split()))
df['char_count'] = df['text'].str.len()
print(df.shape)
"""),
        md("## A. Class distribution"),
        code("""
counts = df['category'].value_counts().sort_values(ascending=False)
plt.figure(figsize=(14,6))
plt.bar(counts.index, counts.values)
plt.xticks(rotation=90)
plt.title('Resume Class Distribution')
plt.tight_layout()
plt.savefig(EDA / 'class_distribution.png', dpi=120)
plt.show()
print(counts)
"""),
        md("## B. Resume word count distribution"),
        code("""
plt.figure(figsize=(10,5))
plt.hist(df['word_count'], bins=60)
plt.axvline(df['word_count'].median(), color='red', linestyle='--', label=f"median={df['word_count'].median():.0f}")
plt.title('Resume Word Count Distribution')
plt.legend(); plt.tight_layout()
plt.savefig(EDA / 'resume_length.png', dpi=120)
plt.show()
print(df['word_count'].describe())
"""),
        md("## C. Character count distribution"),
        code("""
plt.figure(figsize=(10,5))
plt.hist(df['char_count'], bins=60, color='orange')
plt.axvline(df['char_count'].median(), color='red', linestyle='--', label=f"median={df['char_count'].median():.0f}")
plt.title('Resume Character Count Distribution')
plt.legend(); plt.tight_layout()
plt.savefig(EDA / 'character_length.png', dpi=120)
plt.show()
print(df['char_count'].describe())
"""),
        md("""## D/E/F. Top words, bigrams, trigrams
Preprocessing: lowercase, remove URLs/emails, strip markup; filter English stopwords plus common resume boilerplate (experience, skills, responsible, including, using, ...) so analysis isn't dominated by template words."""),
        code("""
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd

BOILERPLATE = {'experience','work','working','skills','skill','responsible','including','using','used','use','strong','good','excellent','knowledge','ability','years','year','team','teams','ability','development','management','customer','support','service','company','position','role','opportunity','professional','environment','responsibilities','required','prefer','etc','provide','provided','also','well','across','within','various','multiple','new','based','including','other','such','like','may','one','two','three','high','low','least','ensure','ensured','assist','assisted','performed','perform','created','developed','maintained','managed','responsible'}

STOP = set(__import__('ml.preprocessing', fromlist=['BASIC_STOPWORDS']).BASIC_STOPWORDS) | BOILERPLATE
texts = df['text'].str.lower()
texts = texts.str.replace(r'https?://\\S+|www\\.\\S+', ' ', regex=True)
texts = texts.str.replace(r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b', ' ', regex=True)
texts = texts.str.replace(r'[^a-z0-9\\+#\\s\\.]', ' ', regex=True)

def top_ngrams(n, topn=25):
    vec = CountVectorizer(ngram_range=(n,n), stop_words=list(STOP), min_df=5, max_df=0.8)
    X = vec.fit_transform(texts)
    freq = X.sum(axis=0).A1
    terms = vec.get_feature_names_out()
    order = np.argsort(freq)[::-1][:topn]
    return pd.Series(freq[order], index=terms[order])

for n, name, fname in [(1,'Top Words','top_words.png'), (2,'Top Bigrams','top_bigrams.png'), (3,'Top Trigrams','top_trigrams.png')]:
    s = top_ngrams(n)
    plt.figure(figsize=(12,6))
    plt.barh(s.index[::-1], s.values[::-1])
    plt.title(name); plt.tight_layout()
    plt.savefig(EDA / fname, dpi=120); plt.show()
"""),
        md("## G. WordCloud (supplementary)"),
        code("""
from wordcloud import WordCloud
corpus = ' '.join(texts.tolist())
wc = WordCloud(width=1200, height=600, background_color='white', max_words=200).generate(corpus)
plt.figure(figsize=(14,7))
plt.imshow(wc); plt.axis('off'); plt.title('Resume WordCloud'); plt.tight_layout()
plt.savefig(EDA / 'wordcloud.png', dpi=120); plt.show()
"""),
        md("## H. Class-wise distinguishing terms (TF-IDF, visualization only)"),
        code("""
from sklearn.feature_extraction.text import TfidfVectorizer
tf = TfidfVectorizer(max_features=5000, stop_words=list(STOP), ngram_range=(1,1))
X = tf.fit_transform(texts)
terms = np.array(tf.get_feature_names_out())
cats = df['category'].values
mean_tfidf = pd.Series(dtype=float)
rows = {}
for cat in sorted(set(cats)):
    rows[cat] = X[cats == cat].mean(axis=0).A1
top_terms = {}
for cat, arr in rows.items():
    top_terms[cat] = terms[np.argsort(arr)[::-1][:10]].tolist()
for cat in list(top_terms)[:8]:
    print(cat, '->', ', '.join(top_terms[cat]))

# plot top terms per a few representative classes
fig, axes = plt.subplots(2, 4, figsize=(18, 8))
for ax, cat in zip(axes.ravel(), list(top_terms)[:8]):
    arr = rows[cat]
    idx = np.argsort(arr)[::-1][:10]
    ax.barh(terms[idx][::-1], arr[idx][::-1])
    ax.set_title(cat)
plt.tight_layout()
plt.savefig(EDA / 'class_keywords.png', dpi=120)
plt.show()
"""),
        md("## Quality report regeneration"),
        code("""
import subprocess
r = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'data' / 'analyze_quality.py')], cwd=ROOT)
print('exit code:', r.returncode)
print((ROOT / 'reports' / 'eda' / 'data_quality.txt').read_text())
"""),
    ],
}

for name, nb in [('01_data_extraction.ipynb', nb1), ('02_eda.ipynb', nb2)]:
    Path(f'notebooks/{name}').write_text(json.dumps(nb, indent=1), encoding='utf-8')
    print('wrote', name)
