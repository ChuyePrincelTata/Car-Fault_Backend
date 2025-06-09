from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import User, Feedback, Mechanic
from schemas import Feedback as FeedbackSchema, FeedbackCreate
from auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=FeedbackSchema)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    feedback = Feedback(
        user_id=current_user.id,
        mechanic_id=feedback_data.mechanic_id,
        diagnostic_id=feedback_data.diagnostic_id,
        rating=feedback_data.rating,
        message=feedback_data.message
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    # Update mechanic rating if feedback is for a mechanic
    if feedback_data.mechanic_id:
        mechanic = db.query(Mechanic).filter(Mechanic.id == feedback_data.mechanic_id).first()
        if mechanic:
            # Recalculate average rating
            all_ratings = db.query(Feedback).filter(
                Feedback.mechanic_id == feedback_data.mechanic_id
            ).all()
            
            total_rating = sum(f.rating for f in all_ratings)
            mechanic.rating = total_rating / len(all_ratings)
            mechanic.total_ratings = len(all_ratings)
            db.commit()
    
    return feedback

@router.get("/", response_model=List[FeedbackSchema])
async def get_feedback(
    mechanic_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Feedback)
    
    if mechanic_id:
        query = query.filter(Feedback.mechanic_id == mechanic_id)
    
    feedback = query.offset(skip).limit(limit).all()
    return feedback

@router.get("/my", response_model=List[FeedbackSchema])
async def get_my_feedback(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    feedback = db.query(Feedback).filter(
        Feedback.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return feedback
