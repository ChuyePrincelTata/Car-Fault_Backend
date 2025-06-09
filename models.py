from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship

from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(str, enum.Enum):
    USER = "user"
    MECHANIC = "mechanic"
    ADMIN = "admin"

class DiagnosticType(str, enum.Enum):
    DASHBOARD = "dashboard"
    ENGINE_SOUND = "engine_sound"
    MANUAL = "manual"

class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    diagnostics = relationship("Diagnostic", back_populates="user")
    feedback_given = relationship("Feedback", foreign_keys="Feedback.user_id", back_populates="user")
    mechanic_profile = relationship("Mechanic", back_populates="user", uselist=False)

class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    business_name = Column(String)
    specialization = Column(String)
    experience_years = Column(Integer)
    phone = Column(String)
    address = Column(Text)
    certificate_url = Column(String)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="mechanic_profile")
    feedback_received = relationship("Feedback", foreign_keys="Feedback.mechanic_id", back_populates="mechanic")

class Diagnostic(Base):
    __tablename__ = "diagnostics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(DiagnosticType))
    title = Column(String)
    description = Column(Text)
    file_url = Column(String)  # For images or audio files
    ai_result = Column(Text)  # JSON string of AI analysis
    confidence_score = Column(Float)
    severity = Column(Enum(SeverityLevel))
    recommendations = Column(Text)  # JSON string
    video_links = Column(Text)  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="diagnostics")

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"), nullable=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.id"), nullable=True)
    rating = Column(Integer)  # 1-5 stars
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="feedback_given")
    mechanic = relationship("Mechanic", foreign_keys=[mechanic_id], back_populates="feedback_received")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    message = Column(Text)
    type = Column(String)  # 'diagnostic_complete', 'mechanic_message', etc.
    read = Column(Boolean, default=False)
    link_id = Column(String, nullable=True)  # Reference to related entity
    created_at = Column(DateTime(timezone=True), server_default=func.now())
