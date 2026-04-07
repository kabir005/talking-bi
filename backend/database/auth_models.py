"""
Authentication Database Models
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.db import Base
import uuid


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships (commented out - not configured in Dataset/Dashboard models)
    # datasets = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")
    # dashboards = relationship("Dashboard", back_populates="owner", cascade="all, delete-orphan")


# Update existing models to add owner relationship
# This will be added to database/models.py
