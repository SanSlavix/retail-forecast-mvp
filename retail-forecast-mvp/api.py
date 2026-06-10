# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import datetime
import joblib
import numpy as np
import pandas as pd
from model_inference import predict

app = FastAPI(title="Retail Forecast API", version="1.0")

class PredictionRequest(BaseModel):
    store_id: int = Field(..., ge=1, le=5)
    sku_id: int = Field(..., ge=1, le=100)
    # Исправлено: 'regex' заменён на 'pattern'
    date: str = Field(..., pattern=r'^\d{4}-\d{2}-\d{2}$')
    price: float = Field(..., gt=0)
    on_promotion: bool = False
    discount_percent: int = Field(0, ge=0, le=50)
    temperature: float = Field(15.0, ge=-30, le=45)

class PredictionResponse(BaseModel):
    forecast_qty: float
    model_version: str = "v1.0"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionResponse)
def predict_endpoint(req: PredictionRequest):
    try:
        # валидация даты
        datetime.datetime.strptime(req.date, "%Y-%m-%d")
        data_dict = req.dict()
        # on_promotion из bool в int
        data_dict['on_promotion'] = int(data_dict['on_promotion'])
        qty = predict(data_dict)
        return {"forecast_qty": round(qty, 1), "model_version": "v1.0"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_predict")
def batch_predict(requests: List[PredictionRequest]):
    results = []
    for req in requests:
        data_dict = req.dict()
        data_dict['on_promotion'] = int(data_dict['on_promotion'])
        qty = predict(data_dict)
        results.append({"input": req.dict(), "forecast_qty": round(qty,1)})
    return {"results": results}
