import pickle
import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.getcwd(), 'data')
PON_DATA_FILE = os.path.join(DATA_DIR, 'pon_data.pkl')
VECTORS_FILE = os.path.join(DATA_DIR, 'pon_gemini_vectors.pkl')

print(f"Checking {PON_DATA_FILE}")
if os.path.exists(PON_DATA_FILE):
    try:
        with open(PON_DATA_FILE, 'rb') as f:
            df = pickle.load(f)
            print("DF Shape:", df.shape)
            print("DF Columns:", df.columns.tolist())
            print("DF Head:", df.head(1).to_dict(orient='records'))
    except Exception as e:
        print(f"Error loading pon_data: {e}")

print(f"Checking {VECTORS_FILE}")
if os.path.exists(VECTORS_FILE):
    try:
        with open(VECTORS_FILE, 'rb') as f:
            vecs = pickle.load(f)
            print("Vectors Type:", type(vecs))
            print("Vectors Shape:", getattr(vecs, 'shape', 'N/A'))
    except Exception as e:
        print(f"Error loading vectors: {e}")
