import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
import json
from .. import schemas
from ..agent import extraction_graph, chat_graph, assessment_graph
from pypdf import PdfReader
import docx2txt

router = APIRouter(prefix="/api/agent", tags=["agent"])

def extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename.lower()
    content_type = file.content_type.lower()
    
    if filename.endswith(".pdf") or "pdf" in content_type:
        try:
            reader = PdfReader(file.file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            if not text.strip():
                raise ValueError("PDF content is empty or scanned (image).")
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
            
    elif filename.endswith(".docx") or "officedocument" in content_type:
        try:
            # Save temporarily in workspace
            temp_dir = os.path.join(os.getcwd(), "temp_files")
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, file.filename)
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            text = docx2txt.process(temp_path)
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return text
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse DOCX: {str(e)}")
            
    elif filename.endswith(".txt") or filename.endswith(".eml") or "text" in content_type or "message" in content_type:
        try:
            contents = file.file.read()
            return contents.decode("utf-8", errors="ignore")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse text/EML file: {str(e)}")
    else:
        # Fallback decode
        try:
            contents = file.file.read()
            return contents.decode("utf-8", errors="ignore")
        except:
            raise HTTPException(status_code=400, detail="Unsupported file format.")

@router.post("/extract-file", response_model=schemas.ComplaintFields)
async def extract_file(file: UploadFile = File(...)):
    text = extract_text_from_file(file)
    if not text.strip():
        raise HTTPException(status_code=400, detail="The uploaded document contains no readable text.")
    
    # Invoke LangGraph extraction
    try:
        inputs = {
            "input_text": text,
            "current_fields": {},
            "chat_history": [],
            "message": None,
            "response": None,
            "suggested_fields": {},
            "assessment_type": None,
            "assessment_result": {}
        }
        res = extraction_graph.invoke(inputs)
        return res["suggested_fields"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Extraction failed: {str(e)}")

@router.post("/extract-text", response_model=schemas.ComplaintFields)
async def extract_text(request: schemas.ExtractionRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
    try:
        inputs = {
            "input_text": request.text,
            "current_fields": {},
            "chat_history": [],
            "message": None,
            "response": None,
            "suggested_fields": {},
            "assessment_type": None,
            "assessment_result": {}
        }
        res = extraction_graph.invoke(inputs)
        return res["suggested_fields"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Extraction failed: {str(e)}")

@router.post("/chat")
async def chat(request: schemas.ChatRequest):
    try:
        inputs = {
            "input_text": "",
            "current_fields": request.current_fields.dict(),
            "chat_history": request.chat_history,
            "message": request.message,
            "response": "",
            "suggested_fields": {},
            "assessment_type": None,
            "assessment_result": {}
        }
        res = chat_graph.invoke(inputs)
        return {
            "response": res["response"],
            "suggested_fields": res["suggested_fields"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Chat processing failed: {str(e)}")

@router.post("/assess")
async def assess(request: schemas.AssessmentRequest):
    try:
        inputs = {
            "input_text": "",
            "current_fields": request.fields.dict(),
            "chat_history": [],
            "message": None,
            "response": None,
            "suggested_fields": {},
            "assessment_type": request.assessment_type,
            "assessment_result": {}
        }
        res = assessment_graph.invoke(inputs)
        return res["assessment_result"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Assessment failed: {str(e)}")
