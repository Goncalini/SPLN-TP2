import json
import numpy as np
from sentence_transformers import SentenceTransformer
from parameters import *

def get_embendiings(model, documents):
    """Precompute document embeddings"""
    print("Calculating results with embeddings")
    
    abstract = [doc['abstract'] for doc in documents]
    doc_embeded = model.encode(abstract, show_progress_bar=True,convert_to_numpy=True)
    
    print("Results calculated")

    return doc_embeded

def get_docss(query, model, documents, doc_embeded, top_k = 10):
    """Retrieve documents for a query"""
    if not documents or doc_embeded is None:
        raise ValueError("Coleção não foi carregada")
    
    print(f"Query: '{query}'")
    
    embbeded_query = model.encode([query], convert_to_numpy=True)[0]
    similarities = similarities = np.dot(doc_embeded, embbeded_query) / (np.linalg.norm(doc_embeded, axis=1) * np.linalg.norm(embbeded_query))
    order_ids = np.argsort(similarities)[::-1]
    
    res = []
    for i in order_ids[:top_k]:
        res.append((documents[i], float(similarities[i])))
    
    return res

def fetch_results(query, model, documents, doc_embeded, top_k = 5):
    """Search and display results"""
    results = get_docss(query, model, documents, doc_embeded, top_k)
    
    print(f"-----------Results-----------")
    
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. SCORE   -  {score:.3f}")
        print(f"TITLE        - {doc['title']}")
        print(f"AUTHORS      - {', '.join(doc.get('authors', []))}")
        print(f"DATE         - {doc.get('date', 'N/A')}")
        print(f"ABSTRACT     -  {doc['abstract'][:300]}...")
        
        if doc.get('keywords'):
            print(f"KEYWORDS     - {', '.join(doc['keywords'][:5])}")
        
        print("-------------")

def search_query_by_user(model, documents, doc_embeded):
    """Interactive search mode."""

    print("User mode activated")
    print("Type 'exit' exit the search mode")
    #print("Query :")
    
    while True:
        query = input("Query: ").strip()
        
        if query.lower() in ['exit']:
            break
        
        if query:
            fetch_results(query, model, documents, doc_embeded, top_k=5)

##############################
################# UTILS ######
##############################

def load_json(path):
    """Load data from JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_model(model_path = MODEL_DIR):
    """Load model for retrieval system."""
    
    try:
        model = SentenceTransformer(model_path)
        print(f"Model successfully loaded from: {model_path}")
    except Exception as e:
        print(f"Failed to load model from: {model_path}")
        print(f"Error: {e}")
        print("Loading base model instead")
        model = SentenceTransformer(BASE_MODEL)
    
    return model

def load_docss(path = JSON_FILE):
    """Load document collection."""
    documents = load_json(path)
    print(f"Loaded {len(documents)} documents")
    return documents

###############################
################### MAIN ######
###############################

def main():
    """Main function for retrieval system"""
    model = load_model()
    documents = load_docss()
    doc_embeded = get_embendiings(model, documents)
    
    test_queries = [
        "artificial intelligence",
        "machine learning",
        "natural language processing",
        "deep learning for image recognition",
        "text classification techniques",
    ]
    
    for query in test_queries:
        fetch_results(query, model, documents, doc_embeded, top_k=3)
        print("------------------------------")

if __name__ == "__main__":
    main()













"""
def evaluate_retrieval_system(test_queries, model, documents, doc_embeded):
    # Evaluate retrieval system.
    print("Evaluating")
    
    precisions = []
    recalls = []
    
    for query_data in test_queries:
        query = query_data['query']
        relevant_docs = set(query_data['relevant_docs'])
        
        results = get_docss(query, model, documents, doc_embeded, top_k=20)
        retrieved_docs = {doc['id'] for doc, _ in results}
        
        if retrieved_docs:
            precision = len(relevant_docs.intersection(retrieved_docs)) / len(retrieved_docs)
            precisions.append(precision)
        
        if relevant_docs:
            recall = len(relevant_docs.intersection(retrieved_docs)) / len(relevant_docs)
            recalls.append(recall)
    
    avg_precision = np.mean(precisions) if precisions else 0.0
    avg_recall = np.mean(recalls) if recalls else 0.0
    f1_score = 2 * avg_precision * avg_recall / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0.0
    
    metrics = {
        'precision': avg_precision,
        'recall': avg_recall,
        'f1_score': f1_score
    }
    
    print("Retrieval Metrics:")
    print(f"  Precision - {metrics['precision']:.3f}")
    print(f"  Recall    - {metrics['recall']:.3f}")
    print(f"  F1-Score  - {metrics['f1_score']:.3f}")
    
    return metrics
"""