from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(BASE_DIR / "model_lightlgbm_fraud.pkl")
features_names = joblib.load(BASE_DIR / "model_features.pkl")

app= FastAPI(
    title="API de Détection de Fraude PaySim",
    description="API permettant de prédire si une transaction financière est frauduleuse.",
    version="1.0.0"
)



class TransactionInput(BaseModel):
    step: int
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    errorBalanceOrig: float
    errorBalanceDest: float
    hour: int
    type_TRANSFER: int

@app.get("/")
def home():
    return{"status": "ok", "message": "Application de détection de fraude opérationnelle."}

@app.post("/predict")
def predict_fraud(transaction: TransactionInput):
    data_dict= transaction.model_dump()
    input_df= pd.DataFrame([data_dict])[features_names]
    prediction= model.predict(input_df)[0]
    probability= model.predict_proba(input_df)[0][1]
    return{
        "is_fraud": int(prediction),
        "fraud_probability": round(float(probability), 4),
        "risk_level": "ÉLEVÉ" if probability > 0.5 else "FAIBLE"
    }