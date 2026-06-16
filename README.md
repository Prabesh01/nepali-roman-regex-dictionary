# Nepali Roman RegEx Dictionary

Perform regex search on nepali and roman words.

Useful for:
- Searching words having certain patterns.
- Look for domain name ideas.
- Get ideas for new born baby's names.

### Generate words list
- `pip install git+https://github.com/Prabesh01/nepali-unicode-converter tqdm`
- `python words-list-generator.py`
- Input: sabdakosh.csv, Output: words.json

### Usage
- Simply serve index.html and words.json over any http server. Cloudflare pages or github pages can also be used.
