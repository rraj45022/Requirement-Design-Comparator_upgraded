from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import json
import yaml
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from pathlib import Path
from app.services.llm_service import get_llm_service
from app.services.chat_service import get_chat_service

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None

app = FastAPI(
    title="Requirements vs Design Comparison API",
    description="FastAPI backend for semantic search and LLM-powered analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    requirements: List[str]
    design: List[str]
    threshold: float = 0.3

class AnalysisResponse(BaseModel):
    requirement: str
    coverage: str
    issue: str
    similarity_score: float

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

def parse_document_content(content: str) -> List[str]:
    """Parse document content and return list of items."""
    # Try JSON
    try:
        data = json.loads(content)
        if isinstance(data, dict):
            items = []
            def recurse(d):
                if isinstance(d, dict):
                    for v in d.values():
                        recurse(v)
                elif isinstance(d, list):
                    for x in d:
                        recurse(x)
                else:
                    items.append(str(d))
            recurse(data)
            return items
        elif isinstance(data, list):
            return [str(i) for i in data]
    except json.JSONDecodeError:
        pass

    # Try YAML
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict):
            items = []
            def recurse(d):
                if isinstance(d, dict):
                    for v in d.values():
                        recurse(v)
                elif isinstance(d, list):
                    for x in d:
                        recurse(x)
                else:
                    items.append(str(d))
            recurse(data)
            return items
        elif isinstance(data, list):
            return [str(i) for i in data]
    except yaml.YAMLError:
        pass

    # Fallback: plain text
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    if len(lines) > 1:
        return lines
    else:
        if nlp:
            doc = nlp(content)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            return [content.strip()]

@app.post("/api/analyze", response_model=List[AnalysisResponse])
async def analyze_documents(request: AnalysisRequest):
    """Perform semantic analysis between requirements and design."""
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        corpus = request.requirements + request.design
        X = vectorizer.fit_transform(corpus)

        req_vecs = X[:len(request.requirements)]
        design_vecs = X[len(request.requirements):]

        feedback = []
        for i, req_vec in enumerate(req_vecs):
            if design_vecs.shape[0] == 0:
                similarity_scores = []
            else:
                similarity_scores = cosine_similarity(req_vec, design_vecs)[0]
            max_sim = max(similarity_scores) if len(similarity_scores) > 0 else 0

            if max_sim >= request.threshold:
                coverage = "Present"
                issue = ""
            else:
                coverage = "Missing"
                issue = "Requirement not found in design"

            feedback.append(AnalysisResponse(
                requirement=request.requirements[i],
                coverage=coverage,
                issue=issue,
                similarity_score=float(max_sim)
            ))
        
        return feedback
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-requirements")
async def upload_requirements(file: UploadFile = File(...)):
    """Upload and parse requirements file."""
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        items = parse_document_content(text_content)
        return {"items": items, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/upload-design")
async def upload_design(file: UploadFile = File(...)):
    """Upload and parse design file."""
    try:
        content = await file.read()
        text_content = content.decode("utf-8")
        items = parse_document_content(text_content)
        return {"items": items, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/chat")
async def chat_with_llm(request: ChatRequest):
    """Chat with LLM for improved feedback."""
    try:
        chat_service = get_chat_service()
        
        if request.conversation_id:
            # Continue existing conversation
            response = chat_service.send_message(request.conversation_id, request.message)
        else:
            # Start new conversation
            conversation_id = chat_service.start_conversation()
            response = chat_service.send_message(conversation_id, request.message)
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/llm-feedback")
async def get_llm_feedback(request: AnalysisRequest):
    """Get LLM-powered feedback after semantic analysis."""
    try:
        # First, perform semantic analysis
        vectorizer = TfidfVectorizer(stop_words='english')
        corpus = request.requirements + request.design
        X = vectorizer.fit_transform(corpus)

        req_vecs = X[:len(request.requirements)]
        design_vecs = X[len(request.requirements):]

        # Create detailed semantic analysis results
        semantic_results = []
        for i, req_vec in enumerate(req_vecs):
            if design_vecs.shape[0] == 0:
                similarity_scores = []
                matched_design_items = []
            else:
                similarity_scores = cosine_similarity(req_vec, design_vecs)[0]
                # Find which design items match this requirement
                matched_design_items = [
                    request.design[j] for j, score in enumerate(similarity_scores)
                    if score >= request.threshold
                ]
            
            max_sim = max(similarity_scores) if len(similarity_scores) > 0 else 0

            semantic_results.append({
                "requirement": request.requirements[i],
                "coverage": "Present" if max_sim >= request.threshold else "Missing",
                "issue": "" if max_sim >= request.threshold else "Requirement not found in design",
                "similarity_score": float(max_sim),
                "matched_design_items": matched_design_items,
                "total_design_items": len(request.design)
            })

        # Get LLM feedback with structured data
        llm_service = get_llm_service()
        feedback = llm_service.generate_improved_feedback(
            parsed_requirements=request.requirements,
            parsed_design=request.design,
            semantic_analysis=semantic_results
        )

        return {
            "semantic_analysis": semantic_results,
            "llm_feedback": feedback,
            "summary": {
                "total_requirements": len(request.requirements),
                "total_design_items": len(request.design),
                "covered_requirements": sum(1 for r in semantic_results if r["coverage"] == "Present"),
                "missing_requirements": sum(1 for r in semantic_results if r["coverage"] == "Missing")
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/{conversation_id}/history")
async def get_chat_history(conversation_id: str):
    """Get conversation history."""
    try:
        chat_service = get_chat_service()
        history = chat_service.get_conversation_history(conversation_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"conversation_id": conversation_id, "messages": history}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/conversations")
async def get_all_conversations():
    """Get list of all conversations."""
    try:
        chat_service = get_chat_service()
        conversations = chat_service.get_conversations_list()
        return {"conversations": conversations}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Requirements vs Design Comparison API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "model_loaded": nlp is not None}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
