from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, JSON
from sqlalchemy.orm import relationship

from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True, nullable=True)
    age = Column(Integer)
    hba1c = Column(Float)
    smoker = Column(Boolean)
    diabetes_duration_years = Column(Integer)
    
    wounds = relationship("Wound", back_populates="patient")

class Wound(Base):
    __tablename__ = "wounds"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    patient_id = Column(String, ForeignKey("patients.id"))
    location = Column(String)

    patient = relationship("Patient", back_populates="wounds")
    assessments = relationship("WoundAssessment", back_populates="wound", order_by="WoundAssessment.day")

class WoundAssessment(Base):
    __tablename__ = "wound_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    wound_id = Column(Integer, ForeignKey("wounds.id"))
    day = Column(Integer, default=0)
    
    # Optional image path
    image_path = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    
    # Store the full JSON analysis here or just critical pieces
    analysis_data = Column(JSON)
    
    wound = relationship("Wound", back_populates="assessments")
