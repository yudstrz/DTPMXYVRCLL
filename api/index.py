from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import json
import math
import requests
from typing import List, Optional
import io
from dotenv import load_dotenv

app = FastAPI()

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
ENV_FILE = os.path.join(PROJECT_ROOT, '.env.local')

print(f"Loading env from {ENV_FILE}")
load_dotenv(ENV_FILE)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Fallback: Manual Parse if load_dotenv fails
if not GEMINI_API_KEY and os.path.exists(ENV_FILE):
    print("GEMINI_API_KEY not found via load_dotenv, trying manual parse...")
    try:
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('GEMINI_API_KEY='):
                    GEMINI_API_KEY = line.strip().split('=', 1)[1]
                    break
    except Exception as e:
         print(f"Manual env parse failed: {e}")

if not GEMINI_API_KEY:
    print("CRITICAL WARNING: GEMINI_API_KEY is still None!")

DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

PON_JSON_FILE = os.path.join(DATA_DIR, 'pon_data.json')
VECTORS_JSON_FILE = os.path.join(DATA_DIR, 'pon_vectors.json')

class ProfileRequest(BaseModel):
    text: str
    top_k: int = 3

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

@app.get("/api/health")
def health():
    return {"status": "ok"}

def load_data():
    pon_data = []
    vectors = []
    
    if os.path.exists(PON_JSON_FILE):
        with open(PON_JSON_FILE, 'r', encoding='utf-8') as f:
            pon_data = json.load(f)
            
    if os.path.exists(VECTORS_JSON_FILE):
        with open(VECTORS_JSON_FILE, 'r', encoding='utf-8') as f:
            vectors = json.load(f)
            
    return pon_data, vectors

def cosine_similarity(vec_a, vec_b):
    # Pure python cosine similarity
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def get_gemini_embedding(text: str):
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not set")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "models/text-embedding-004",
        "content": {
             "parts": [{"text": text}]
        },
        "taskType": "RETRIEVAL_QUERY"
    }
    
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        raise Exception(f"Gemini API Error: {resp.text}")
        
    result = resp.json()
    if 'embedding' not in result:
        raise Exception(f"Invalid response from Gemini: {result}")
        
    return result['embedding']['values']

def get_gemini_chat_response(message: str, history: List[dict]):
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY not set")
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    contents = []
    for msg in history:
        role = "user" if msg['role'] == 'user' else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg['content']}]
        })
        
    # Add current message
    contents.append({
        "role": "user",
        "parts": [{"text": message}]
    })
    
    data = {
        "contents": contents
    }
    
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        raise Exception(f"Gemini API Error: {resp.text}")
        
    result = resp.json()
    try:
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        return text_response
    except (KeyError, IndexError):
        raise Exception(f"Unexpected response format: {result}")

@app.post("/api/match-profile")
async def match_profile(req: ProfileRequest):
    pon_data, vectors = load_data()
    
    if not pon_data or not vectors:
        return {"error": "Database not found. Please run scripts/convert_data.py locally."}
    
    if len(pon_data) != len(vectors):
         min_len = min(len(pon_data), len(vectors))
         pon_data = pon_data[:min_len]
         vectors = vectors[:min_len]

    # Embed User Query
    try:
        query_vec = get_gemini_embedding(req.text)
    except Exception as e:
        return {"error": f"Embedding error: {str(e)}"}
    
    # Calculate Scores
    scores = []
    for idx, vec in enumerate(vectors):
        score = cosine_similarity(query_vec, vec)
        scores.append((idx, score))
    
    # Top K
    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = scores[:req.top_k]
    
    results = []
    for idx, score in top_indices:
        row = pon_data[idx]
        results.append({
            "id": row.get('OkupasiID', 'N/A'),
            "nama": row.get('Okupasi', 'N/A'),
            "score": float(score),
            "gap": "Skill Gap Analysis requires detailed comparison." # Placeholder
        })
        
    return {"recommendations": results}

@app.post("/api/chat")
async def chat_career(req: ChatRequest):
    try:
        response_text = get_gemini_chat_response(req.message, req.history)
        return {"response": response_text}
    except Exception as e:
        return {"error": str(e)}

# Parsing Support
from pypdf import PdfReader
import docx

@app.post("/api/parse-cv")
async def parse_cv(file: UploadFile = File(...)):
    text = ""
    filename = file.filename.lower()
    
    content = await file.read()
    file_io = io.BytesIO(content)
    
    try:
        if filename.endswith('.pdf'):
            reader = PdfReader(file_io)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif filename.endswith('.docx'):
            doc = docx.Document(file_io)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith('.txt'):
            text = content.decode('utf-8')
    except Exception as e:
        return {"error": str(e)}
        
    return {"text": text.strip()}

@app.get("/api/courses")
def get_courses():
    courses_path = os.path.join(DATA_DIR, 'courses.json')
    if os.path.exists(courses_path):
        with open(courses_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
