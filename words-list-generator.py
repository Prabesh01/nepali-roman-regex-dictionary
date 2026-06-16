import csv
import json
import os
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from nepali_unicode_converter import ReverseConverter, ReverseConverterV2

# Worker initialization function to instantiate converters per-process safely
def init_worker():
    global rev, rev2, smart_rev, smart_rev2
    rev = ReverseConverter()
    rev2 = ReverseConverterV2()
    smart_rev = ReverseConverter(smart=True)
    smart_rev2 = ReverseConverterV2(smart=True)

# Main processing unit for a single word
def process_word(nepali_word):
    # 1. Generate all 4 variants
    val_v1 = rev.convert(nepali_word)
    val_v2 = rev2.convert(nepali_word)
    val_v3 = smart_rev.convert(nepali_word)
    val_v4 = smart_rev2.convert(nepali_word) # v2-smart

    variants_map = {
        'v1': val_v1,
        'v2': val_v2,
        'v3': val_v3,
        'v4': val_v4
    }

    # 2. Find the most repeated string (The Standard)
    counts = Counter(variants_map.values())
    max_count = max(counts.values())

    # Get all strings that tied for the max count
    candidates = [val for val, count in counts.items() if count == max_count]

    # 3. Apply Tie-Breaker
    if val_v4 in candidates:
        standard_val = val_v4
    elif val_v3 in candidates:
        standard_val = val_v3
    elif val_v2 in candidates:
        standard_val = val_v2
    else:
        standard_val = val_v1

    # 4. Build compressed block
    entry = {
        "nepali": nepali_word,
        "standard": standard_val
    }

    # 5. Diffs execution
    for key, string_val in variants_map.items():
        if string_val != standard_val:
            entry[key] = string_val

    return entry

if __name__ == '__main__':
    words_list = []
    
    # Read words into memory quickly
    print("Reading CSV file...")
    with open('sabdakosh.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None) # Skip header
        for row in reader:
            if row and row[1].strip():
                if len(row[1].strip().split())==1:
                    words_list.append(row[1].strip())

    total_words = len(words_list)
    optimized_dictionary = []

    # Process words in parallel using available CPU cores
    num_workers = os.cpu_count()
    print(f"Starting compression engine using {num_workers} CPU cores...")
    
    with ProcessPoolExecutor(max_workers=num_workers, initializer=init_worker) as executor:
        # map handles task distribution and maintains progress tracking context
        results = list(tqdm(
            executor.map(process_word, words_list), 
            total=total_words, 
            desc="Processing dictionary"
        ))
        optimized_dictionary.extend(results)

    # Export
    print("Saving compressed JSON dataset...")
    with open('words.json', 'w', encoding='utf-8') as outfile:
        json.dump(optimized_dictionary, outfile, ensure_ascii=False, separators=(',', ':'))

    print(f"\n✨ Successfully compressed {len(optimized_dictionary)} words!")
