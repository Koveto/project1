import json
import os

# Path to this file's directory
BASE_DIR = os.path.dirname(__file__)
ITEMS_PATH = os.path.join(BASE_DIR, "smt_items.json")

with open(ITEMS_PATH, "r") as f:
    SMT_ITEMS = json.load(f)
