from fastapi import FastAPI
from pydantic import BaseModel,Field
import json 
import joblib


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


@app.get("/")
def root():
    return {"message": "AYUVA backend is running"}


@app.post("/predict")
def predict(vitals : PatientVitals):
    input_data = [[getattr(vitals,feat) for feat in feature_order]]
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]

    return {
        "risk_level" : "high" if prediction ==1 else "low",
        "probability" : round(float(probability),4)
    }



@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}