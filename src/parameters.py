# Configuration constants
REPOSITORIUM_URL = "https://repositorium.sdum.uminho.pt/oai/oai"

COLLECTIONS = {"msc_di": "col_1822_21316", "msc": "col_1822_2"}

METADATA_PREFIX = "dim"
BATCH_SIZE = 100
RECORDS_NUMBER = 1000

BATCH = 16
EPOCHS = 5
BASE_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
# BASE_MODEL = "distiluse-base-multilingual-cased-v2"
# BASE_MODEL = "all-MiniLM-L6-v2"
THRESHOLD_SIMILARITY = 0.35


MIN_ABST = 50
MAX_ABST = 2000
KEYWORD_THRESHOLD_MAX = 2 #mais comuns
KEYWORD_THRESHOLD_MIN = 5 #mais raras

TIMEOUT = 45
RETRIES_CAP = 10
DELAY = 1.0
MAX_ERRORS = 10

XML_FILE = "./dataset/initial_extract.xml"
JSON_FILE = "./dataset/result.json"
TRAIN_FILE = "./dataset/similarities.json"
MODEL_DIR = "models"
DATASET_DIR = "dataset"

print("--------Loaded parameters------------")
