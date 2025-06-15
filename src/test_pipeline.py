import os, nltk
from parameters import *
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Import functions from other modules
from retrievel import retrieve_collections
from xml_to_json import xml_to_json, save_json
from get_similarity import filter_collections_for_train, save_data_trained
from model import upload_data_trained, train_modell, test_model, save_trained_model
from search_engine import load_model, load_docss, get_embendiings, search_query_by_user, get_docss

def setup_directories():
    """Setup required directories."""
    #checkfoldr("datasets")
    checkfoldr(DATASET_DIR)
    checkfoldr(MODEL_DIR)

def first_script():
    """Extract data from repositories."""
    print("----------------------------------------")
    print("Script retrievel.py")
    print("----------------------------------------")
    
    xml_data = retrieve_collections(COLLECTIONS, max_records=RECORDS_NUMBER)

    path = XML_FILE

    checkfoldr(os.path.dirname(path))
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(xml_data)
        
    print(f"Records saved at {path}")
    
    return xml_data

def second_script():
    """Process extracted data."""
    print("----------------------------------------")
    print("Script xml_to_json.py")
    print("----------------------------------------")
    
    documents = xml_to_json()
    save_json(documents)
    print(f"Saved at {JSON_FILE}")
    
    return documents

def third_script(documents):
    """Calculate document similarities."""
    print("----------------------------------------")
    print("Script get_similarities.py")
    print("----------------------------------------")
    
    pars_train = filter_collections_for_train(documents)
    save_data_trained(pars_train)
    
    return pars_train

def forth_script():
    """Train the sentence transformer model."""
    print("----------------------------------------")
    print("Script model.py")
    print("----------------------------------------")
    
    data_trainx = upload_data_trained()
    
    if data_trainx:
        split_idx = int(0.8 * len(data_trainx)) #Calcula 80% do tamanho da lista data_trainx e armazena esse valor como um índice inteiro.
        trained_ex = data_trainx[:split_idx]
        text_ex = data_trainx[split_idx:]
        
        model = train_modell(trained_ex)
        
        if text_ex:
            test_model(model, text_ex)
        
        save_trained_model(model)
        
        return model
    else:
        print("No model found")
        return None

def final_script():
    """Test the retrieval system."""
    print("----------------------------------------")
    print("Script search_engine.py")
    print("----------------------------------------")
    
    model = load_model()
    documents = load_docss()
    document_embeddings = get_embendiings(model, documents)
    
    test_queries = [
        "artificial intelligence",
        "machine learning",
        "natural language processing",
        "deep learning for image recognition",
        "text classification techniques",
    ]
    
    for query in test_queries:
        print(f"Teste com query: '{query}'")
        results = get_docss(query, model, documents, document_embeddings, top_k=3)
        
        for i, (doc, score) in enumerate(results, 1):
            print(f"{i}. [{score:.3f}] {doc['title'][:80]}...")

def interactive_search():
    """Start interactive search mode."""
    model = load_model()
    documents = load_docss()
    document_embeddings = get_embendiings(model, documents)
    
    search_query_by_user(model, documents, document_embeddings)


###############################
################# UTILS #######
###############################

def checkfoldr(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)




###############################
################### MAIN ######
###############################


def main():
    """Main orchestration function."""

    print("Checking NLTK resources...")
    # Check and download 'punkt'
    try:
        nltk.data.find('tokenizers/punkt')
        print("Resource 'punkt' found.")
    except LookupError:
        print("Resource 'punkt' not found. Downloading...")
        nltk.download('punkt')
        print("Download of 'punkt' completed.")

    # Check and download 'punkt_tab'
    try:
        nltk.data.find('tokenizers/punkt_tab')
        print("Resource 'punkt_tab' found.")
    except LookupError:
        print("Resource 'punkt_tab' not found. Downloading...")
        nltk.download('punkt_tab')
        print("Download of 'punkt_tab' completed.")

    # Check and download 'stopwords'
    try:
        nltk.data.find('corpora/stopwords')
        print("Resource 'stopwords' found.")
    except LookupError:
        print("Resource 'stopwords' not found. Downloading...")
        nltk.download('stopwords')
        print("Download of 'stopwords' completed.")

    print("All required NLTK resources are available. Starting")
    
    setup_directories()
    
    if not os.path.exists(JSON_FILE):
        print("Didnt found any data, retrieving data from repositorium")
        
        if not os.path.exists(XML_FILE):
            first_script()
        
        documents = second_script()
        
        if len(documents) > 1:
            third_script(documents)
        
        if os.path.exists(TRAIN_FILE):
            forth_script()
    
    else:
        print("Found data, skipping data extraction and processing steps")
    
    if os.path.exists(JSON_FILE):
        final_script()
        #print("Chegouuu")
        print("\n")
        response = input("Do you wish to test your own queries (y/n): ")
        if response.lower() in ['yes', 'y']:
            interactive_search()
    
    print("Exiting!")

if __name__ == "__main__":
    main()
