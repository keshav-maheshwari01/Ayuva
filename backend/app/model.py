from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Boolean
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)


class Patient(Base):
    __tablename__ = 'patients'
    patientid = Column(Integer, primary_key=True, nullable=False)
    patientname = Column(String, nullable=False)
    patientage = Column(Integer, nullable=False)
    gender = Column(String)
    address = Column(String)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)


class Visit(Base):
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.patientid"), nullable=False)
    asha_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    age_year = Column(Float, nullable=False)
    ap_hi = Column(Integer, nullable=False)
    ap_lo = Column(Integer, nullable=False)
    cholesterol = Column(Float, nullable=False)
    gluc = Column(Integer, nullable=False)
    smoke = Column(Boolean, nullable=False)
    alco = Column(Boolean, nullable=False)
    active = Column(Boolean, nullable=False)
    bmi = Column(Float, nullable=False)
    pulse_pressure = Column(Integer, nullable=False)
    map = Column(Float, nullable=False)


class Predictions(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True, nullable=False)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)
    risk_level = Column(String, nullable=False)
    probability = Column(Float, nullable=False)
    shap_explanation = Column(String, nullable=False)


class Referrals(Base):
    __tablename__ = 'referrals'
    id = Column(Integer, primary_key=True, nullable=False)
    visit_id = Column(Integer, ForeignKey("visits.id"), nullable=False)
    status = Column(String, nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    doctor_decision = Column(String, nullable=True)
    doctor_notes = Column(String, nullable=True)