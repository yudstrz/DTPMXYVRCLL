from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import pickle
import google.generativeai as genai
import numpy as np
import pandas as pd
from typing import List, Optional
import io
# import PyPDF2 # If needed, but lets try to keep it light or use it if installed
# import docx

app = FastAPI()

# Config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

DATA_DIR = os.path.join(os.getcwd(), 'data')
PON_DATA_FILE = os.path.join(DATA_DIR, 'pon_data.pkl')
VECTORS_FILE = os.path.join(DATA_DIR, 'pon_gemini_vectors.pkl')

class ProfileRequest(BaseModel):
    text: str
    top_k: int = 3

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []

@app.get("/api/health")
def health():
    return {"status": "ok"}

def get_vectors_and_df():
    # Load DataFrame
    if not os.path.exists(PON_DATA_FILE):
        return None, None
    
    with open(PON_DATA_FILE, 'rb') as f:
        df_pon = pickle.load(f)

    # Check for vectors
    if os.path.exists(VECTORS_FILE):
        with open(VECTORS_FILE, 'rb') as f:
            vectors = pickle.load(f)
        return df_pon, vectors
    
    # Generate Vectors (One-time / Cache)
    # Note: In a real serverless env, this might timeout if dataset is huge.
    # Assuming valid small dataset for this demo.
    print("Generating Gemini Embeddings...")
    texts = (
         "Okupasi: " + df_pon['Okupasi'].astype(str) + ". " +
         "Unit Kompetensi: " + df_pon['Unit_Kompetensi'].astype(str) + ". " +
         "Keterampilan: " + df_pon['Kuk_Keywords'].astype(str)
    ).tolist()
    
    vectors = []
    # Batch processing to avoid limits? For now sequential.
    for text in texts:
        emb = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        vectors.append(emb['embedding'])
    
    vectors = np.array(vectors)
    
    # Save cache (Attempt to save, might be ephemeral in Vercel)
    try:
        with open(VECTORS_FILE, 'wb') as f:
            pickle.dump(vectors, f)
    except:
        pass # Read-only file system
        
    return df_pon, vectors

@app.post("/api/match-profile")
async def match_profile(req: ProfileRequest):
    df_pon, vectors = get_vectors_and_df()
    if df_pon is None or vectors is None:
        return {"error": "Database not found"}
    
    # Embed User Query
    query_emb = genai.embed_content(
        model="models/embedding-001",
        content=req.text,
        task_type="retrieval_query"
    )['embedding']
    
    query_vec = np.array(query_emb)
    
    # Cosine Similarity
    # (A . B) / (|A| * |B|)
    norm_vectors = np.linalg.norm(vectors, axis=1)
    norm_query = np.linalg.norm(query_vec)
    
    scores = np.dot(vectors, query_vec) / (norm_vectors * norm_query)
    
    # Top K
    top_indices = np.argsort(scores)[::-1][:req.top_k]
    
    results = []
    for idx in top_indices:
        row = df_pon.iloc[idx]
        results.append({
            "id": row.get('OkupasiID', 'N/A'),
            "nama": row.get('Okupasi', 'N/A'),
            "score": float(scores[idx]),
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
    response = chat.send_message(req.message)
    
    return {"response": response.text}

# Parsing Support (Simplified for now)
# To fully implement, need to install pypdf/python-docx
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
