from fastapi import FastAPI,Depends
from app.auth import get_current_user, require_role
from pydantic import BaseModel,Field
import json 
import joblib
from app.database import Sessionmaker
from app.model import Predictions , Patient,Visit,User ,Referrals
from app.auth import hashing ,verify_password  , create_access_token

import shap

import os 


app = FastAPI()

model = joblib.load("D:/AYUVA/ml/models/cardio_risk_model.pkl")
with open("D:/AYUVA/ml/models/feature_order.json","r") as f : 
    feature_order = json.load(f)

explainer = shap.TreeExplainer(model)

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




class UserSignup(BaseModel):
    name : str 
    username : str 
    password : str 
    role : str 

class UserLogin(BaseModel):
    username :str
    password : str 





class ReferralOut(BaseModel):
    id : int 
    visit_id : int 
    status : str 
    doctor_id : int |None
    doctor_decision : str | None 
    doctor_notes : str | None

    class config :
        from_attributes = True 




class ReferralUpdate(BaseModel):
    doctor_decision : str 
    doctor_notes : str 


@app.get("/")
def root():
    return {"message": "AYUVA backend is running"}


@app.post("/predict")
def predict(request : PredictRequest , current_user: dict = Depends(require_role("asha"))):
    db = Sessionmaker()
    visit = db.query(Visit).filter(Visit.id == request.visit_id).first()
    if visit is None :  
        db.close()
        return {"error"  :"visit not found"}

    input_data = [[getattr(visit,feat) for feat in feature_order]]
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]
    risk_level= "high" if prediction == 1 else "low"
    shap_values =  explainer.shap_values(input_data)
    shap_dict = {feat : round(float(val),4) for feat,val in zip(feature_order,shap_values[0])}
    shap_explanation = json.dumps(shap_dict)
    

    new_prediction = Predictions(
        visit_id = visit.id,    
        risk_level = risk_level,
        probability = float(probability),
        shap_explanation = shap_explanation   #update needed later 
    )
    if risk_level == "high" :
        new_referral = Referrals(
            visit_id = visit.id , 
            status = "pending",
            doctor_id = None,
            doctor_decision = None , 
            doctor_notes = None 
        )
        db.add(new_referral)
        db.commit()

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    db.close()

    return {
        "risk_level"  : risk_level,
        "probability"  : round(float(probability),4),
        "saved_id"  : new_prediction.id}



@app.post("/patient")
def patient(patient : PatientCreate ,current_user: dict = Depends(require_role("asha"))):
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
def visit(visit : VisitCreate , current_user: dict = Depends(require_role("asha"))):
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
def get_patient_visits(patient_id:int , current_user: dict = Depends(get_current_user)):
    db = Sessionmaker()
    visits = db.query(Visit).filter(Visit.patient_id==patient_id).all()
    db.close()
    return visits



@app.get("/patients")
def get_all_patients(current_user: dict = Depends(get_current_user)):
    db = Sessionmaker()
    patients = db.query(Patient).all()
    db.close()
    return patients


@app.get("/predictions/{visit_id}")

def get_prediction(visit_id : int , current_user: dict = Depends(get_current_user)):
    db = Sessionmaker()
    prediction = db.query(Predictions).filter(Predictions.visit_id == visit_id).first()
    db.close()
    return prediction








@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}





@app.post("/signup")
def signup(user : UserSignup) : 
    db = Sessionmaker()
    existing = db.query(User).filter(User.username == user.username ).first()
    if existing :
        db.close()
        return {"error": "Username already taken"}


    new_user = User(
        name = user.name,
        username = user.username,
        password_hash = hashing(user.password),
        role = user.role

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()


    return {"id": new_user.id, "username": new_user.username, "role": new_user.role}


        




@app.post("/login")
def login (credentials : UserLogin):
    db = Sessionmaker()
    user = db.query(User).filter(User.username == credentials.username).first()
    db.close()

    if user is None : 
        return {"error": "Invalid username or password"}

    if not verify_password(credentials.password, user.password_hash):
        return {"error": "Invalid username or password"}

    token = create_access_token(data = {"user_id" : user.id , "role" : user.role})


    return {
        "access_token" : token , 
        "token_type": "bearer",
        "role"  : user.role
    }



@app.get("/referrals")
def get_referrals(current_user : dict = Depends(require_role("doctor"))):
    db = Sessionmaker()
    referrals = db.query(Referrals).filter(Referrals.status =='pending').all()
    db.close()
    return referrals


@app.put("/referrals/{referral_id}")
def update_referral(referral_id : int , update :ReferralUpdate , current_user :dict = Depends(require_role("doctor"))):
    db = Sessionmaker()
    referral = db.query(Referrals).filter(Referrals.id == referral_id).first()
    if referral is None : 
        db.close()
        return {"error": "referral not found"}

    referral.doctor_id = current_user["user_id"]
    referral.doctor_decision=update.doctor_decision
    referral.doctor_notes = update.doctor_notes
    referral.status = "reviewed"
    db.commit()
    db.refresh(referral)
    db.close()
    return {"id": referral.id, "status": referral.status, "message": "Referral updated"}