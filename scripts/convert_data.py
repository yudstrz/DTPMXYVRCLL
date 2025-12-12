import pickle
import os
import pandas as pd
import numpy as np
import json
import google.generativeai as genai
from dotenv import load_dotenv

DATA_DIR = os.path.join(os.getcwd(), 'data')
PON_DATA_FILE = os.path.join(DATA_DIR, 'pon_data.pkl')
VECTORS_FILE = os.path.join(DATA_DIR, 'pon_gemini_vectors.pkl')

PON_JSON_FILE = os.path.join(DATA_DIR, 'pon_data.json')
VECTORS_JSON_FILE = os.path.join(DATA_DIR, 'pon_vectors.json')
ENV_FILE = os.path.join(os.getcwd(), '.env.local')

def convert_data():
    if os.path.exists(ENV_FILE):
        print(f"Loading env from {ENV_FILE}")
        # Try different encodings
        try:
            load_dotenv(ENV_FILE, encoding='utf-8')
        except UnicodeDecodeError:
            print("UTF-8 failed, trying UTF-16...")
            try:
                load_dotenv(ENV_FILE, encoding='utf-16')
            except UnicodeDecodeError:
                 print("UTF-16 failed, trying latin-1...")
                 load_dotenv(ENV_FILE, encoding='latin-1')
    else:
        print("No .env.local found, relying on system env vars")

    print("Starting conversion...")
    
    df = None
    
    # Convert DataFrame to JSON
    if os.path.exists(PON_DATA_FILE):
        print(f"Loading {PON_DATA_FILE}...")
        try:
            with open(PON_DATA_FILE, 'rb') as f:
                df = pickle.load(f)
            
            # Ensure it is a DataFrame
            if isinstance(df, pd.DataFrame):
                df = df.fillna("")
                data_list = df.to_dict(orient='records')
                
                with open(PON_JSON_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data_list, f, ensure_ascii=False, indent=2)
                print(f"Saved {len(data_list)} records to {PON_JSON_FILE}")
            else:
                print("Error: Pon data is not a pandas DataFrame")

        except Exception as e:
            print(f"Error loading/converting pon_data: {e}")
            return # Cannot proceed without data
    else:
        print(f"File not found: {PON_DATA_FILE}")
        return

    # Handle Vectors
    vecs_list = []
    if os.path.exists(VECTORS_FILE):
        print(f"Loading {VECTORS_FILE}...")
        try:
            with open(VECTORS_FILE, 'rb') as f:
                vecs = pickle.load(f)
            if isinstance(vecs, np.ndarray):
                vecs_list = vecs.tolist()
            elif isinstance(vecs, list):
                vecs_list = vecs
        except Exception as e:
            print(f"Error loading vectors: {e}")
    
    if not vecs_list:
        print("Vectors missing or empty. Generating new embeddings...")
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY not found in environment!")
            for k in os.environ:
                if 'GEMINI' in k:
                    print(f"Found similar key: {k}")
            return

        genai.configure(api_key=api_key)
        
        if df is not None:
            # Logic from api/index.py
            texts = (
                 "Okupasi: " + df['Okupasi'].astype(str) + ". " +
                 "Unit Kompetensi: " + df['Unit_Kompetensi'].astype(str) + ". " +
                 "Keterampilan: " + df['Kuk_Keywords'].astype(str)
            ).tolist()
            
            print(f"Generating embeddings for {len(texts)} items...")
            vectors = []
            for i, text in enumerate(texts):
                if i % 10 == 0:
                    print(f"Processed {i}/{len(texts)}")
                try:
                    emb = genai.embed_content(
                        model="models/embedding-001",
                        content=text,
                        task_type="retrieval_document"
                    )
                    vectors.append(emb['embedding'])
                except Exception as e:
                    print(f"Error embedding item {i}: {e}")
                    # Fallback? or break?
                    vectors.append([0.0]*768) # Placeholder to avoid shape mismatch
            
            vecs_list = vectors
            print("Generation complete.")
            
            # Save vectors to json immediately
            if vecs_list:
                with open(VECTORS_JSON_FILE, 'w', encoding='utf-8') as f:
                    json.dump(vecs_list, f)
                print(f"Saved vectors to {VECTORS_JSON_FILE}. Count: {len(vecs_list)}")

    elif vecs_list:
         # Vectors existed in pickle, just save to json
        with open(VECTORS_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(vecs_list, f)
        print(f"Saved vectors to {VECTORS_JSON_FILE}. Count: {len(vecs_list)}")

if __name__ == "__main__":
    convert_data()
