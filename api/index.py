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

def preprocess_text(text: str) -> list:
    """Convert text to a list of lowercase alphanumeric words."""
    # Simple tokenization: remove non-alphanumeric, lowercase, split
    tokens = re.findall(r'\w+', text.lower())
    # Filter out very short tokens (1-2 chars) and common stop words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been', 'being'}
    tokens = [t for t in tokens if len(t) > 2 and t not in stop_words]
    return tokens

def calculate_match_score(user_tokens: list, occupation: dict) -> float:
    """Calculate weighted match score between user tokens and occupation keywords."""
    # Extract fields with different weights
    occ_name = occupation.get('Okupasi', '')
    unit_kompetensi = occupation.get('Unit_Kompetensi', '')
    kuk_keywords = occupation.get('Kuk_Keywords', '')
    
    # Tokenize each field separately
    name_tokens = set(preprocess_text(occ_name))
    unit_tokens = set(preprocess_text(unit_kompetensi))
    kuk_tokens = set(preprocess_text(kuk_keywords))
    
    user_token_set = set(user_tokens)
    
    # Calculate matches with weights
    name_matches = len(user_token_set.intersection(name_tokens))
    unit_matches = len(user_token_set.intersection(unit_tokens))
    kuk_matches = len(user_token_set.intersection(kuk_tokens))
    
    # Weighted scoring (name is most important, then keywords, then unit)
    weighted_score = (name_matches * 3.0) + (kuk_matches * 2.0) + (unit_matches * 1.5)
    
    # Normalize by total possible matches (with weights)
    max_possible = (len(name_tokens) * 3.0) + (len(kuk_tokens) * 2.0) + (len(unit_tokens) * 1.5)
    
    if max_possible == 0:
        return 0.0
    
    # Calculate percentage and boost it for better UX (multiply by 100 for percentage)
    raw_score = (weighted_score / max_possible) * 100
    
    # Apply a boost factor to make scores more meaningful (square root to compress high scores)
    # This makes low scores higher and keeps high scores reasonable
    boosted_score = min(100, raw_score * 1.5)
    
    return boosted_score / 100  # Return as 0-1 for consistency

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
