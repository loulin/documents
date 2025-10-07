import csv
import os

DRUG_DATA = []
DRUG_LOOKUP = {}

def load_drug_data(csv_path: str):
    global DRUG_DATA, DRUG_LOOKUP
    if DRUG_DATA: # Already loaded
        return

    print(f"--- Loading drug data from {csv_path} ---")
    try:
        with open(csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                DRUG_DATA.append(row)
                # Create lookup by common name and generic name
                drug_name = row.get('药品名称')
                generic_name = row.get('通用名')
                if drug_name: DRUG_LOOKUP[drug_name.lower()] = row
                if generic_name: DRUG_LOOKUP[generic_name.lower()] = row
        print(f"--- Successfully loaded {len(DRUG_DATA)} drugs. ---")
    except FileNotFoundError:
        print(f"--- ERROR: Drug CSV file not found at {csv_path} ---")
    except Exception as e:
        print(f"--- ERROR loading drug data: {e} ---")

def get_drug_info(name: str) -> dict:
    return DRUG_LOOKUP.get(name.lower(), {})

# Path to the drug CSV file relative to the project root
DRUG_CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                             '01_主题验证', '05_药物管理', 'Medicines', '新增药品数据库_125种_交付版.csv')

# Load data on import
load_drug_data(DRUG_CSV_PATH)
