import re, os, json, unicodedata
import xml.etree.ElementTree as ET
from parameters import *

def xml_to_json(xml_path = XML_FILE):
    """Convert XML data to JSON format."""
    print("Converting XML file into JSON file")

    documents = []
    
    namespaces = {
        'oai': 'http://www.openarchives.org/OAI/2.0/',
        'dim': 'http://www.dspace.org/xmlns/dspace/dim'
    }
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []
    records = root.findall('.//oai:record', namespaces)
    
    for i, record in enumerate(records):
        fille = read_xml2(record, namespaces)
        if fille:
            if is_valid_doc(fille):
                #print("teste entrei")
                documents.append(fille)
                
        #imprimir de 100 em 100
        if (i + 1) % 100 == 0:
            print(f"Converted {i + 1} records")
    
    n_valid_docs = len(documents)
    print(f"Conversion completed with {n_valid_docs} valid documents")
    return documents

def read_xml2(record, namespaces):
    """Process a single record from XML."""
    try:
        metadata = record.find('.//dim:dim', namespaces)
        if metadata is None:
            return None
        
        fille = {
            'id': get_idd(record, namespaces),
            'title': get_info(metadata, 'title', namespaces),
            'abstract': get_info(metadata, 'description', namespaces, 'abstract'),
            'authors': get_info2(metadata, 'contributor', namespaces, 'author'),
            'keywords': get_info2(metadata, 'subject', namespaces),
            'date': get_info(metadata, 'date', namespaces, 'issued'),
            'type': get_info(metadata, 'type', namespaces),
            'language': get_info(metadata, 'language', namespaces, 'iso'),
            'subjects_udc': get_info2(metadata, 'subject', namespaces, 'udc'),
            'subjects_fos': get_info2(metadata, 'subject', namespaces, 'fos'),
            'collections': get_info2(metadata, 'relation', namespaces, 'ispartof')
        }
        
        fille = arrange_data(fille)
        
        return fille
        
    except Exception as e:
        print(f"Error {e}")
        return None

def get_idd(record, namespaces):
    """Extract identifier from record."""
    header = record.find('.//oai:header', namespaces)
    if header is not None:
        idd = header.find('oai:identifier', namespaces)
        if idd is not None:
            return idd.text if idd.text else ""
    return ""

def get_info(metadata, element, namespaces, qualifier = None):
    """Extract a single field from metadata."""
    prefix = f".//dim:field[@element='{element}']"
    if qualifier:
        prefix += f"[@qualifier='{qualifier}']"
    
    field = metadata.find(prefix, namespaces)
    #return field.text if field is not None and field.text else ""
    if field is not None and field.text:
        return field.text
    else:
        return ""

def get_info2(metadata, element, namespaces, qualifier = None):
    """Extract multiple fields from metadata."""
    prefix = f".//dim:field[@element='{element}']"
    if qualifier:
        prefix += f"[@qualifier='{qualifier}']"
    
    fields = metadata.findall(prefix, namespaces)
    #result = [field.text for field in fields if field.text]
    result = []
    for field in fields:
        if field.text:
            result.append(field.text)
    return result

def arrange_data(fille):
    """Clean document data."""
    camps = ['title', 'abstract']
    for field in camps:
        if fille.get(field):
            fille[field] = clean_text(fille[field])
    
    list_fields = ['authors', 'keywords', 'subjects_udc', 'subjects_fos', 'collections']
    for field in list_fields:
        if fille.get(field):
            fille[field] = [clean_text(item) for item in fille[field] if item]
    
    if fille.get('date'):
        fille['date'] = normalize_data(fille['date'])
    
    return fille

def normalize_data(date):
    """Normalize date string to extract year."""
    match = re.search(r'\b(19|20)\d{2}\b', date)
    #return match.group() if match else date
    if match:
        return match.group()
    else:
        return date

def is_valid_doc(fille, min = MIN_ABSTRACT_LENGTH, max = MAX_ABSTRACT_LENGTH):
    """Check if document is valid for processing."""
    if not fille.get('title'):
        return False
    
    if not fille.get('abstract'):
        return False
    
    lenght = len(fille['title'])

    if lenght < min:
        return False
    
    if lenght > max:
        return False
    
    return True

"""

def save_data(documents, path = JSON_FILE):
    #Save collection to JSON file.
    save_json(documents, path)
    print(f"Saved at {path}")
"""

#################################
################# UTILS #########
#################################

def checkfoldr(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(data, path = JSON_FILE):
    """Save data to JSON file."""
    checkfoldr(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(path):
    """Load data from JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return ""
    
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text



##############################
################  MAIN #######
##############################


def main():
    """Main function for data processing."""
    print("Starting XML to JSON conversion")
    documents = xml_to_json()
    save_json(documents)
    print(f"Saved at {JSON_FILE}")


if __name__ == "__main__":
    main()
