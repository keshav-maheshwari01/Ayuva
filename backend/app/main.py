from fastapi import FastAPI
from pydantic import BaseModel,Field
import json 
import joblib
from app.database import Sessionmaker
from app.model import Predictions , Patient,Visit

app = FastAPI()

model = joblib.load("D:/AYUVA/ml/models/cardio_risk_model.pkl")
with open("D:/AYUVA/ml/models/feature_order.json","r") as f : 
    feature_order = json.load(f)


class PatientVitals(BaseModel):
    age_year: float = Field(..., ge=1, le=120)
    ap_hi: int = Field(..., ge=50, le=250)
    ap_lo: int = Field(..., ge=30, le=200)
    cholesterol: int = Field(..., ge=1, le=3)
    gluc: int = Field(..., ge=1, le=3)
    smoke: int = Field(..., ge=0, le=1)
    alco: int = Field(..., ge=0, le=1)
    active: int = Field(..., ge=0, le=1)
    bmi: float = Field(..., ge=10, le=80)
    pulse_pressure: int = Field(..., ge=0, le=150)
    map: float = Field(..., ge=30, le=200)


class PatientCreate(BaseModel):
    patientname :str
    patientage : int = Field(...,ge=0,le=120)
    gender : str 
    address  : str 
    created_by : int 



class VisitCreate(PatientVitals,BaseModel):
    patient_id : int 
    asha_id :int



class PredictRequest(BaseModel):
    visit_id : int

@app.get("/")
def root():
    return {"message": "AYUVA backend is running"}


@app.post("/predict")
def predict(request : PredictRequest):
    db = Sessionmaker()
    visit = db.query(Visit).filter(Visit.id == request.visit_id).first()
    if visit is None :  
        db.close()
        return {"error"  :"visit not found"}

    input_data = [[getattr(visit,feat) for feat in feature_order]]
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]
    risk_level= "high" if prediction == 1 else "low"

    

    new_prediction = Predictions(
        visit_id = visit.id,    
        risk_level = risk_level,
        probability = float(probability),
        shap_explanation = "placeholder"   #update needed later 
    )

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    db.close()

    return {
        "risk_level"  : risk_level,
        "probability"  : round(float(probability),4),
        "saved_id"  : new_prediction.id}



@app.post("/patient")
def patient(patient : PatientCreate):
    db = Sessionmaker()
    new_patient = Patient( 
        patientname = patient.patientname,
        patientage = patient.patientage,
        gender = patient.gender,
        address = patient.address,
        created_by = patient.created_by)

    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    db.close()

    return {
        "id":new_patient.patientid , "message" : "Patient created successfully"}


@app.post("/visit")
def visit(visit : VisitCreate):
    db = Sessionmaker()
    new_visit = Visit(
        patient_id = visit.patient_id,
        asha_id = visit.asha_id,
        age_year = visit.age_year,
        ap_hi = visit.ap_hi,
        ap_lo = visit.ap_lo,
        cholesterol = visit.cholesterol , 
        gluc = visit.gluc,
        smoke = visit.smoke,
        alco = visit.alco,
        active = visit.active,
        bmi = visit.bmi,
        pulse_pressure = visit.pulse_pressure ,
        map = visit.map)

    db.add(new_visit)
    db.commit()
    db.refresh(new_visit)
    db.close()

    return {
        "id": new_visit.id,
        "message": "Visit recorded successfully"}




@app.get("/patients/{patient_id}/visits")
def get_patient_visits(patient_id:int):
    db = Sessionmaker()
    visits = db.query(Visit).filter(Visit.patient_id==patient_id).all()
    db.close()
    return visits



@app.get("/patients")
def get_all_patients():
    db = Sessionmaker()
    patients = db.query(Patient).all()
    db.close()
    return patients


@app.get("/predictions/{visit_id}")

def get_prediction(visit_id : int):
    db = Sessionmaker()
    prediction = db.query(Predictions).filter(Predictions.visit_id == visit_id).first()
    db.close()
    return prediction








@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}