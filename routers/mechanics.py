from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from database import get_db
from models import User, Mechanic, VerificationStatus
from schemas import Mechanic as MechanicSchema, MechanicCreate, MechanicUpdate
from auth import get_current_active_user
from config import settings

router = APIRouter()

@router.get("/", response_model=List[MechanicSchema])
async def get_mechanics(
    skip: int = 0,
    limit: int = 100,
    verified_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(Mechanic)
    if verified_only:
        query = query.filter(Mechanic.verification_status == VerificationStatus.APPROVED)
    
    mechanics = query.offset(skip).limit(limit).all()
    return mechanics

@router.get("/me", response_model=MechanicSchema)
async def get_my_mechanic_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "mechanic":
        raise HTTPException(status_code=403, detail="Not a mechanic")
    
    mechanic = db.query(Mechanic).filter(Mechanic.user_id == current_user.id).first()
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic profile not found")
    
    return mechanic

@router.put("/me", response_model=MechanicSchema)
async def update_mechanic_profile(
    mechanic_data: MechanicUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "mechanic":
        raise HTTPException(status_code=403, detail="Not a mechanic")
    
    mechanic = db.query(Mechanic).filter(Mechanic.user_id == current_user.id).first()
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic profile not found")
    
    # Update fields
    for field, value in mechanic_data.dict(exclude_unset=True).items():
        setattr(mechanic, field, value)
    
    db.commit()
    db.refresh(mechanic)
    return mechanic

@router.post("/upload-certificate")
async def upload_certificate(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "mechanic":
        raise HTTPException(status_code=403, detail="Not a mechanic")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "application/pdf"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(settings.upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Update mechanic profile
    mechanic = db.query(Mechanic).filter(Mechanic.user_id == current_user.id).first()
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic profile not found")
    
    mechanic.certificate_url = file_path
    mechanic.verification_status = VerificationStatus.PENDING
    db.commit()
    
    return {"message": "Certificate uploaded successfully", "file_path": file_path}

@router.get("/{mechanic_id}", response_model=MechanicSchema)
async def get_mechanic(
    mechanic_id: int,
    db: Session = Depends(get_db)
):
    mechanic = db.query(Mechanic).filter(Mechanic.id == mechanic_id).first()
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    
    return mechanic
