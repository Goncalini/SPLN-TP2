import os, json, nltk, random, re, time
import numpy as np
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from parameters import *

def get_keyworrds(doc, frequency_kw):
    """Get filtered keywords for a document."""
    keywords = set()
    
    keywordss = extract_keywords(doc.get('abstract', ''))
    keywords.update(keywordss)
    
    keyword_camp = [kw.lower() for kw in doc.get('keywords', [])]
    keywords.update(keyword_camp)
    
    filtered_keywords = set()
    for kw in keywords:
        freq = frequency_kw.get(kw, 0)
        if freq > 0.01 and freq < 0.5:
            filtered_keywords.add(kw)
    
    return filtered_keywords

def filter_collections_for_train(documents):
    """Create training collection from documents."""
    print("Filtering collections for training")
    
    frequency_kw = keyword_freq(documents)
    
    num_docs = len(documents)
    total_pairs = num_docs * (num_docs - 1) // 2
    
    print(f"Calculating similaries for {total_pairs}")
    
    pairs = []
    counte = 0
    for i, doc1 in enumerate(documents):
        for _, doc2 in enumerate(documents[i+1:], i+1):
            sim = calc_similiraty(doc1, doc2, frequency_kw)
            
            if sim >= THRESHOLD_SIMILARITY:
                pairs.append((doc1['abstract'], doc2['abstract'], sim))
                #print("appended...............")
            counte += 1
            #print("testeee")
            if counte % 1000 == 0: #imrprimir de 1000 em 1000
                print(f"Processed {counte} out of {total_pairs} ")
    
    print(f"Completed similarity calculations for {len(pairs)} pairs")
    return pairs

def calc_keyword_similarity(doc1, doc2, frequency_kw):
    """Calculate keyword similarity between documents."""
    keywords_doc1 = get_keyworrds(doc1, frequency_kw)
    keywords_doc2 = get_keyworrds(doc2, frequency_kw)
    
    if not keywords_doc1 or not keywords_doc2:
        return 0.0
    
    intersection = keywords_doc1.intersection(keywords_doc2)
    if not intersection:
        return 0.0
    
    value = 0.0
    for keyword in intersection:
        aux = frequency_kw.get(keyword, 0.5)
        rarity_weight = 1.0 - aux
        value = value + rarity_weight
    
    doc1_len = len(keywords_doc1)
    doc2_len = len(keywords_doc2)

    max_keywords = max(doc1_len, doc2_len)
    normal_value = value / max_keywords
    
    res = normalize_score(normal_value)

    return res

def keyword_freq(documents):
    """Calculate keyword frequencies across documents."""
    print("Searching Keyword frequency")
    
    doc_count = len(documents)

    keyword_count = Counter()
    for doc in documents:
        keywordss = extract_keywords(doc.get('abstract', ''))
       
        keyword_camp = []
        for kw in doc.get('keywords', []):
            keyword_camp.append(kw.lower())
        
        total_keywords = set(keywordss).union(keyword_camp)
        
        for keyword in total_keywords:
            keyword_count[keyword] += 1
   
    frequency_kw = dict(map(lambda item: (item[0], item[1] / doc_count), keyword_count.items()))
    
    length_f = len(frequency_kw)

    print(f"Frequency - {length_f} keywords found")
    return frequency_kw


def lists_similarity(s1, s2):
    """Calculate similarity between subject lists."""

    set1 = set()
    set2 = set()

    if not s1 or not s2:
        return 0.0
    
    for s in s1:
        set1.add(s.lower())

    for s in s2:
        set2.add(s.lower())
    
    res = calculate_jaccard_similarity(set1, set2)

    return res

def get_col_sim(doc1, doc2):
    """Calculate similarity between document collections."""
    col1 = doc1.get('collections', [])
    col2 = doc2.get('collections', [])

    if not col1 or not col2:
        return 0.0
    
    set1 = set()
    set2 = set()
    
    for c in col1:
        set1.add(c.lower())

    for c in col2:
        set2.add(c.lower())
    
    res = calculate_jaccard_similarity(set1, set2)

    return res

def calc_similiraty(doc1, doc2, frequency_kw):
    """Calculate similarity between two documents."""
    sim = []
    
    # Keyword similarity (weighted 0.4)
    keyword_sim = calc_keyword_similarity(doc1, doc2, frequency_kw)
    sim.append(keyword_sim * 0.45)

    # UDC subjects similarity (weighted 0.3)
    udc_sim = lists_similarity(doc1.get('subjects_udc', []), doc2.get('subjects_udc', []))
    sim.append(udc_sim * 0.25)

    # FOS subjects similarity (weighted 0.2)
    fos_sim = lists_similarity(doc1.get('subjects_fos', []), doc2.get('subjects_fos', []))
    sim.append(fos_sim * 0.2)

    # Collection similarity (weighted 0.1)
    collection_sim = get_col_sim(doc1, doc2)
    sim.append(collection_sim * 0.1)

    # Sum weighted similarities
    total_sim = sum(sim)

    # Normalize and return
    return normalize_score(total_sim)
    

#############################
########### UTILS ###########
#############################

def checkfoldr(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(data, path):
    """Save data to JSON file."""
    checkfoldr(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path):
    """Load data from JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def save_data_trained(pairs, path = TRAIN_FILE):
    """Save training data to JSON file"""
    train_data = [
        {
            'text1': pair[0],
            'text2': pair[1],
            'similarity': pair[2]
        }
        for pair in pairs
    ]
    
    save_json(train_data, path)
    print(f"Trained data saved at {path}")

def extract_keywords(text, language = 'portuguese'):
    """Extract keywords from text"""
    if not text:
        return []
    
    tokens = word_tokenize(text.lower())
    
    try:
        stop_words = set(stopwords.words(language))
    except:
        stop_words = set(stopwords.words('english'))
    
    keywords = [
        token for token in tokens 
        if token.isalpha() and len(token) > 2 and token not in stop_words
    ]
    
    return keywords

def calculate_jaccard_similarity(set1, set2):
    """Calculate Jaccard similarity between two sets"""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def normalize_score(score, min_val = 0.0, max_val = 1.0):
    """Normalize score to specified range."""
    return max(min_val, min(max_val, score))


###################################
################### MAIN ##########
###################################

def main():
    """Main function for similarity calculation."""

    # Checck NLTK data 
    print("Checking NLTK data")
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    print("NLTK data is ready")

    documents = load_json(JSON_FILE)
    print(f"Loaded {len(documents)} documents")
    
    pairs = filter_collections_for_train(documents)
    save_data_trained(pairs)
    
    print("-----------STATISTICS------------")

    if pairs:
        sim = [pair[2] for pair in pairs]
        print("\nSimilarity Statistics:")
        print(f"  Mean similarity       -    {np.mean(sim):.2f}")
        print(f"  Median similarity     -    {np.median(sim):.2f}")
        print(f"  Std deviation         -    {np.std(sim):.2f}")
        print(f"  Maximum similarity    -    {np.max(sim):.2f}")
        print(f"  Minimum similarity    -    {np.min(sim):.2f}")
    else:
        print("Nothing to display.")

if __name__ == "__main__":
    main()
