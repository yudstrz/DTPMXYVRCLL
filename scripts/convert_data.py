import pickle
import os
import pandas as pd
import numpy as np
import json
import requests
import time
from dotenv import load_dotenv

DATA_DIR = os.path.join(os.getcwd(), 'data')
PON_DATA_FILE = os.path.join(DATA_DIR, 'pon_data.pkl')
VECTORS_FILE = os.path.join(DATA_DIR, 'pon_gemini_vectors.pkl')

PON_JSON_FILE = os.path.join(DATA_DIR, 'pon_data.json')
VECTORS_JSON_FILE = os.path.join(DATA_DIR, 'pon_vectors.json')
ENV_FILE = os.path.join(os.getcwd(), '.env.local')

def get_embedding(text, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "models/text-embedding-004",
        "content": {
             "parts": [{"text": text}]
        },
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code != 200:
            print(f"API Error {resp.status_code}: {resp.text}")
            return [0.0] * 768
            
        result = resp.json()
        if 'embedding' not in result:
             return [0.0] * 768
             
        return result['embedding']['values']
    except Exception as e:
        print(f"Request failed: {e}")
        return [0.0] * 768

def convert_data():
    if os.path.exists(ENV_FILE):
        print(f"Loading env from {ENV_FILE}")
        load_dotenv(ENV_FILE)
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not in env, trying manual parse...")
        try:
            with open(ENV_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.strip().split('=', 1)[1]
                        break
        except Exception as e:
            print(f"Manual parse failed: {e}")

    if not api_key:
        print("ERROR: GEMINI_API_KEY not found.")
        return
    
    print(f"Using API Key: {api_key[:5]}...")

    print("Starting conversion and embedding generation...")
    
    df = None
    if os.path.exists(PON_DATA_FILE):
        with open(PON_DATA_FILE, 'rb') as f:
            df = pickle.load(f)
            
        if isinstance(df, pd.DataFrame):
            df = df.fillna("")
            data_list = df.to_dict(orient='records')
            
            with open(PON_JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_list, f, ensure_ascii=False, indent=2)
            print(f"Saved {len(data_list)} records to {PON_JSON_FILE}")
            
            # Generate Embeddings
            texts = (
                 "Okupasi: " + df['Okupasi'].astype(str) + ". " +
                 "Unit Kompetensi: " + df['Unit_Kompetensi'].astype(str) + ". " +
                 "Keterampilan: " + df['Kuk_Keywords'].astype(str)
            ).tolist()
            
            print(f"Generating new embeddings for {len(texts)} items (using text-embedding-004)...")
            vectors = []
            
            for i, text in enumerate(texts):
                if i % 5 == 0:
                    print(f"Processing {i}/{len(texts)}...")
                
                vec = get_embedding(text, api_key)
                vectors.append(vec)
                time.sleep(0.5) # Avoid rate limits
                
            # Save vectors
            with open(VECTORS_JSON_FILE, 'w', encoding='utf-8') as f:
                json.dump(vectors, f)
            print(f"Saved {len(vectors)} vectors to {VECTORS_JSON_FILE}")
            
    else:
        print(f"File not found: {PON_DATA_FILE}")

    # Extract Courses
    xlsx_path = os.path.join(DATA_DIR, 'DTP_Database.xlsx')
    courses_json_path = os.path.join(DATA_DIR, 'courses.json')
    
    if os.path.exists(xlsx_path):
        print(f"Extracting courses from {xlsx_path}...")
        try:
            df_courses = pd.read_excel(xlsx_path, sheet_name='Course_Maxy')
            df_courses = df_courses.fillna("")
            
            # Standardize columns for frontend
            courses_list = []
            for _, row in df_courses.iterrows():
                courses_list.append({
                    "title": row.get('Nama_Course', 'Unknown Course'),
                    "provider": "Maxy Academy",
                    "level": row.get('Level', 'All Levels'),
                    "duration": row.get('Duration', 'Self-paced'),
                    "image": row.get('Image_URL', 'https://placehold.co/600x400/orange/white?text=Maxy+Course'),
                    "url": row.get('URL', '#')
                })
                
            with open(courses_json_path, 'w', encoding='utf-8') as f:
                json.dump(courses_list, f, indent=2)
            print(f"Saved {len(courses_list)} courses to {courses_json_path}")
            
        except Exception as e:
            print(f"Error extracting courses: {e}")
    else:
        print(f"Excel file not found: {xlsx_path}")

if __name__ == "__main__":
    convert_data()
