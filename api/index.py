from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import json
import re
from typing import List, Optional
import io
# Removed dotenv and requests as they were mainly for Gemini

app = FastAPI()

# Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PON_JSON_FILE = os.path.join(DATA_DIR, 'pon_data.json')

class ProfileRequest(BaseModel):
    text: str
    top_k: int = 3

@app.get("/api/health")
def health():
    return {"status": "ok"}

def load_data():
    pon_data = []
    if os.path.exists(PON_JSON_FILE):
        with open(PON_JSON_FILE, 'r', encoding='utf-8') as f:
            pon_data = json.load(f)
    return pon_data

def preprocess_text(text: str) -> set:
    """Convert text to a set of unique lowercase alphanumeric words."""
    # Simple tokenization: remove non-alphanumeric, lowercase, split
    tokens = re.findall(r'\w+', text.lower())
    # Fiter out common stop words if needed, for now just use set
    return set(tokens)

def calculate_match_score(user_tokens: set, occupation: dict) -> float:
    """Calculate a simplistic overlap score between user tokens and occupation keywords."""
    # Combine relevant fields from occupation
    occ_text = f"{occupation.get('Okupasi', '')} {occupation.get('Unit_Kompetensi', '')} {occupation.get('Kuk_Keywords', '')}"
    occ_tokens = preprocess_text(occ_text)
    
    if not occ_tokens:
        return 0.0
        
    # Intersection count
    intersection = user_tokens.intersection(occ_tokens)
    
    # Jaccard Similarity (Intersection / Union)
    union = user_tokens.union(occ_tokens)
    if not union:
        return 0.0
        
    return len(intersection) / len(union)

@app.post("/api/match-profile")
async def match_profile(req: ProfileRequest):
    pon_data = load_data()
    
    if not pon_data:
        return {"error": "Database not found. Please ensure data/pon_data.json exists."}

    user_tokens = preprocess_text(req.text)
    
    if not user_tokens:
         return {"error": "No valid text found in profile to analyze."}

    # Calculate Scores
    scores = []
    for row in pon_data:
        score = calculate_match_score(user_tokens, row)
        scores.append((row, score))
    
    # Top K
    scores.sort(key=lambda x: x[1], reverse=True)
    top_results = scores[:req.top_k]
    
    results = []
    for row, score in top_results:
        results.append({
            "id": row.get('OkupasiID', 'N/A'),
            "nama": row.get('Okupasi', 'N/A'),
            "score": float(score), # Normalize for display if needed, but Jaccard is 0-1
            "gap": "Match based on keyword overlap." 
        })
        
    return {"recommendations": results}

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
