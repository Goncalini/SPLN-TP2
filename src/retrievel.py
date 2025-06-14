import requests, time, os, random
import xml.etree.ElementTree as ET
from parameters import *

def retrieve_collections(collections, max_records = RECORDS_NUMBER, url = REPOSITORIUM_URL):
    """Extract data from multiple collections."""
    print(f"Extracting {max_records} records from collections: {list(collections.keys())}")
    print("----------------------")
    estates_dic = {}
    final_content = '<?xml version="1.0" encoding="UTF-8"?>\n<collection>\n'

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    

    records_fetched = 0
    for name, c_id in collections.items():
        if records_fetched >= max_records:
            print(f"{max_records} were retrieved successfully.")
            break
            
        records_aux = max_records - records_fetched # Calculate remaining records to fetch
        print(f"Getting {records_aux} from collection: {name} ({c_id})")
        print("----------------------")
        
        try:
            collection_xml, all_records = get_collection(c_id, records_aux, url, session)
            if all_records > 0:
                #collecion_records = read(collection_xml)
                collection_records = collection_xml
                final_content = final_content + collection_records
                records_fetched = records_fetched + all_records
                estates_dic[name] = all_records
                
                print(f"Successfully extracted {all_records} records from '{name}'.")
                print(f"Fetched {records_fetched} out of {max_records} records extracted so far.")
                
                if records_fetched >= max_records:
                    print(f"Total of {max_records} records reached. Stopping extraction.")
            else:
                print(f"Nothing found {name}")
                estates_dic[name] = 0
                
        except Exception as e:
            print(f"Error {e}")
            estates_dic[name] = 0
            continue

    final_content += '</collection>'
    
    print("\n")
    print("---------------------------------------------")

    for name, i in estates_dic.items():
        print(f"{name}: {i}")
    
    return final_content

def get_collection(c_id, max_records, url, session):
    """Extract data from a single collection."""

    collection_records = ""
    resumption_token = None

    end = "noRecordsMatch"

    n_records = 0
    fails_counter = 0
    while n_records < max_records:
        if resumption_token:
            params = {
                "verb": "ListRecords",
                "resumptionToken": resumption_token
            }
        else:
            params = {
                "verb": "ListRecords",
                "metadataPrefix": METADATA_PREFIX,
                "set": c_id
            }

        bool = False

        # Retry logic with exponential backoff 
        for trial in range(3):
            try:
                if trial > 0:
                    delay = (2 ** trial) + random.uniform(0, 1)
                    print(f"Trying {trial + 1}")
                    time.sleep(delay)
                
                response = session.get(url, params=params, timeout=TIMEOUT)
                response.raise_for_status()
                response_xml = response.text
                bool = True
                fails_counter = 0
                break
                
            except requests.RequestException as e:
                print(f"Error {trial + 1}: {e}")
                if trial == 2:
                    fails_counter += 1

        if not bool:
            if fails_counter >= MAX_ERRORS:
                print("Aborting retrieval")
                break
            else:
                continue
        

        if end in response_xml:
            print(f"End of records for collection {c_id}")
            break
        
        # Parse the XML response
        try:
            root = ET.fromstring(response_xml)
            records = root.findall(".//{http://www.openarchives.org/OAI/2.0/}record")
            
            response_counter = 0
            for record in records:
                response_counter = response_counter + 1
                collection_records = collection_records + ET.tostring(record, encoding='unicode') + '\n'

                n_records = n_records + 1
                if n_records >= max_records:
                    break

            print(f"--⬇️ Getting {response_counter} records" + "\n" + f"--🔄️ Total {n_records}")

            rt_elem = root.find(".//{http://www.openarchives.org/OAI/2.0/}resumptionToken")
            if rt_elem is not None and rt_elem.text:
                resumption_token = rt_elem.text.strip()
                
                delay = DELAY + random.uniform(0, 0.5)
                time.sleep(delay)
            else:
                print(f" End of records.")
                break

        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            fails_counter += 1
            if fails_counter >= MAX_ERRORS:
                break
            continue

    return collection_records, n_records

"""
def read_xml(final_content):
    ## Extract records from XML content
    return final_content

def save_xml_data(final_content, path = XML_FILE):
    #Save XML content to file
    checkfoldr(os.path.dirname(path))
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"\n📂 Records saved at {path}")
"""

################################################
################################ UTILS #########
################################################

def checkfoldr(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)


######################################
########################## MAIN ######
######################################

def main():
    """Main function for data extraction."""
    xml_data = retrieve_collections(COLLECTIONS, max_records=RECORDS_NUMBER)
    #save_xml_data(xml_data)
    
    path = XML_FILE

    checkfoldr(os.path.dirname(path))
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(xml_data)
        
    print(f"Records saved at {path}")

    print("Concluded!")

if __name__ == "__main__":
    main()
