from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import json
import math
import google.generativeai as genai
from typing import List, Optional
import io

app = FastAPI()

# Config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DATA_DIR = os.path.join(os.getcwd(), 'data')
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

@app.post("/api/match-profile")
async def match_profile(req: ProfileRequest):
    pon_data, vectors = load_data()
    
    if not pon_data or not vectors:
        return {"error": "Database not found. Please run scripts/convert_data.py locally."}
    
    if len(pon_data) != len(vectors):
         # If size mismatch (maybe fallback or just trim?)
         # For now, just warn or trim to shortest
         min_len = min(len(pon_data), len(vectors))
         pon_data = pon_data[:min_len]
         vectors = vectors[:min_len]

    # Embed User Query
    try:
        query_emb_resp = genai.embed_content(
            model="models/embedding-001",
            content=req.text,
            task_type="retrieval_query"
        )
        query_vec = query_emb_resp['embedding']
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
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Construct history
    history_gemini = []
    for msg in req.history:
        history_gemini.append({
            "role": "user" if msg['role'] == 'user' else "model",
            "parts": [msg['content']]
        })
    
    chat = model.start_chat(history=history_gemini)
    try:
        response = chat.send_message(req.message)
        return {"response": response.text}
    except Exception as e:
        return {"error": str(e)}

# Parsing Support (Removing dependencies if possible, but pypdf/python-docx are smaller than pandas)
# Keeping them for now unless further optimization needed.
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
            # python-docx
            doc = docx.Document(file_io)
            text = "\n".join([p.text for p in doc.paragraphs])
        elif filename.endswith('.txt'):
            text = content.decode('utf-8')
    except Exception as e:
        return {"error": str(e)}
        
    return {"text": text.strip()}
