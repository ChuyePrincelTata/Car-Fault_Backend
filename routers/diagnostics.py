from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import uuid
import json
from database import get_db
from models import User, Diagnostic, DiagnosticType
from schemas import Diagnostic as DiagnosticSchema, DiagnosticCreate, DiagnosticResult
from auth import get_current_active_user
from config import settings

router = APIRouter()

@router.post("/", response_model=DiagnosticSchema)
async def create_diagnostic(
    diagnostic_data: DiagnosticCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    diagnostic = Diagnostic(
        user_id=current_user.id,
        type=diagnostic_data.type,
        title=diagnostic_data.title,
        description=diagnostic_data.description
    )
    
    db.add(diagnostic)
    db.commit()
    db.refresh(diagnostic)
    
    return diagnostic

@router.post("/upload-file/{diagnostic_id}")
async def upload_diagnostic_file(
    diagnostic_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get diagnostic
    diagnostic = db.query(Diagnostic).filter(
        Diagnostic.id == diagnostic_id,
        Diagnostic.user_id == current_user.id
    ).first()
    
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    # Validate file type based on diagnostic type
    if diagnostic.type == DiagnosticType.DASHBOARD:
        allowed_types = ["image/jpeg", "image/png"]
    elif diagnostic.type == DiagnosticType.ENGINE_SOUND:
        allowed_types = ["audio/mpeg", "audio/wav", "audio/mp3"]
    else:
        raise HTTPException(status_code=400, detail="File upload not supported for this diagnostic type")
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Create upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update diagnostic
    diagnostic.file_url = file_path
    db.commit()
    
    # TODO: Send to AI model for analysis
    # For now, return mock result
    mock_result = {
        "issue": "Check Engine Light" if diagnostic.type == DiagnosticType.DASHBOARD else "Engine Knock",
        "confidence": 85.5,
        "description": "Mock AI analysis result",
        "recommendation": "Please consult a mechanic",
        "severity": "medium",
        "video_links": [
            {"title": "How to fix this issue", "url": "https://youtube.com/watch?v=example"}
        ]
    }
    
    diagnostic.ai_result = json.dumps(mock_result)
    diagnostic.confidence_score = mock_result["confidence"]
    diagnostic.severity = mock_result["severity"]
    db.commit()
    
    return {"message": "File uploaded and analyzed successfully", "result": mock_result}

@router.get("/", response_model=List[DiagnosticSchema])
async def get_my_diagnostics(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    diagnostics = db.query(Diagnostic).filter(
        Diagnostic.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return diagnostics

@router.get("/{diagnostic_id}", response_model=DiagnosticSchema)
async def get_diagnostic(
    diagnostic_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    diagnostic = db.query(Diagnostic).filter(
        Diagnostic.id == diagnostic_id,
        Diagnostic.user_id == current_user.id
    ).first()
    
    if not diagnostic:
        raise HTTPException(status_code=404, detail="Diagnostic not found")
    
    return diagnostic
