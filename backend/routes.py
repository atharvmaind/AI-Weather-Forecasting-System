from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

try:
    from . import models
    from .database import get_db
    from .predict import forecast_next_n
    from .predict import predict_from_features
    from .schemas import PastWeatherResponse, PredictRequest, PredictResponse, TrainResponse, RealWeatherResponse
    from .train import train_from_csv
    from .ml_utils import LastKnown
    from .ml_utils import make_target_features
    from .weather_api import fetch_real_weather
    from .weather_api import fetch_past_weather
except ImportError:  # pragma: no cover
    import models  # type: ignore
    from database import get_db  # type: ignore
    from predict import forecast_next_n  # type: ignore
    from predict import predict_from_features  # type: ignore
    from schemas import PastWeatherResponse, PredictRequest, PredictResponse, TrainResponse, RealWeatherResponse  # type: ignore
    from train import train_from_csv  # type: ignore
    from ml_utils import LastKnown  # type: ignore
    from ml_utils import make_target_features  # type: ignore
    from weather_api import fetch_real_weather  # type: ignore
    from weather_api import fetch_past_weather  # type: ignore


router = APIRouter()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT_DIR / "data" / "weather.csv"


@router.get("/past-weather", response_model=PastWeatherResponse)
def past_weather(city: str, start_date: date):
    """
    Dynamic past weather: fetch previous 7 days from Open-Meteo (archive API).
    Returns days [start_date-7 .. start_date-1].
    """
    try:
        items = fetch_past_weather(city=city, start_date=str(start_date), days=7)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch past weather: {e}")

    # Convert to schema shape (date as date)
    out = []
    for it in items:
        out.append(
            {
                "date": pd.to_datetime(it["date"]).date(),
                "temperature": float(it["temperature"]),
                "humidity": float(it["humidity"]),
                "rain": str(it["rain"]),
            }
        )
    return {"items": out}


@router.post("/train-model", response_model=TrainResponse)
def train_model(db: Session = Depends(get_db)):
    if not DATASET_PATH.exists():
        raise HTTPException(status_code=404, detail="Dataset not found. Expected data/weather.csv")

    df = pd.read_csv(DATASET_PATH)
    df.columns = [c.lower() for c in df.columns]
    df["date"] = pd.to_datetime(df["date"]).dt.date
    df["rain"] = df["rain"].astype(int).astype(bool)

    # Upsert-ish: insert if date not present
    existing_dates = set(
        d for (d,) in db.execute(select(models.WeatherData.date)).all()
    )
    to_add = []
    for _, row in df.iterrows():
        if row["date"] in existing_dates:
            continue
        to_add.append(
            models.WeatherData(
                date=row["date"],
                temperature=float(row["temperature"]),
                humidity=float(row["humidity"]),
                pressure=float(row["pressure"]),
                wind_speed=float(row["wind_speed"]),
                rain=bool(row["rain"]),
            )
        )
    if to_add:
        db.add_all(to_add)
        db.commit()

    result = train_from_csv(str(DATASET_PATH))
    return {"rows_loaded": int(result["rows"]), "trained": bool(result["trained"])}


@router.get("/real-weather", response_model=RealWeatherResponse)
def real_weather(city: str, start_date: date | None = None, days: int = 7):
    if start_date is None:
        start_date = date.today()
    items = fetch_real_weather(city=city, start_date=str(start_date), days=int(days))
    return {"items": items}


@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest, db: Session = Depends(get_db)):
    try:
        # We need lag-1 features, so fetch one extra day before start_date.
        start_prev = req.start_date - timedelta(days=1)
        real_range = fetch_real_weather(city=req.city, start_date=str(start_prev), days=req.days + 1)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch real weather: {e}")

    real_by_date = {it["date"]: it for it in real_range}

    target_dates: list[date] = [req.start_date + timedelta(days=i) for i in range(req.days)]
    prev_rows: list[LastKnown] = []
    real_for_targets: list[dict] = []

    for d in target_dates:
        prev_d = d - timedelta(days=1)
        prev = real_by_date.get(prev_d.isoformat())
        cur = real_by_date.get(d.isoformat())
        if prev is None or cur is None:
            raise HTTPException(status_code=400, detail="Real weather data missing for lag computation.")
        prev_rows.append(
            LastKnown(
                last_date=prev_d,
                temperature=float(prev["temperature"]),
                humidity=float(prev["humidity"]),
                pressure=float(prev["pressure"]),
                wind_speed=float(prev["wind_speed"]),
                rain=1 if prev["rain"] else 0,
            )
        )
        real_for_targets.append(cur)

    try:
        x = make_target_features(target_dates=target_dates, prev_rows=prev_rows)
        temp_pred, hum_pred, rain_proba = predict_from_features(x)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Models not trained. Call /train-model first.")

    items: list[dict] = []
    for i, d in enumerate(target_dates):
        real = real_for_targets[i]
        proba = float(rain_proba[i])
        pred_yes = proba >= 0.5
        real_icon = str(real.get("weather_icon") or "Cloudy")
        predicted_icon = "Rainy" if pred_yes else ("Sunny" if float(temp_pred[i]) >= 25.0 else "Cloudy")

        # store predictions (replace if exists for same date)
        existing = (
            db.execute(select(models.Prediction).where(models.Prediction.date == d))
            .scalars()
            .first()
        )
        if existing:
            existing.predicted_temp = float(temp_pred[i])
            existing.predicted_humidity = float(hum_pred[i])
            existing.rain_prediction = bool(pred_yes)
            existing.rain_probability = proba
        else:
            db.add(
                models.Prediction(
                    date=d,
                    predicted_temp=float(temp_pred[i]),
                    predicted_humidity=float(hum_pred[i]),
                    rain_prediction=bool(pred_yes),
                    rain_probability=proba,
                )
            )

        items.append(
            {
                "date": d,
                "real_temperature": float(real["temperature"]),
                "real_humidity": float(real["humidity"]),
                "predicted_temperature": float(np.round(temp_pred[i], 2)),
                "predicted_humidity": float(np.round(hum_pred[i], 2)),
                "real_weather_icon": real_icon,
                "predicted_weather_icon": predicted_icon,
                "rain_probability": proba,
                "rain_prediction": "Yes" if pred_yes else "No",
                "real_rain": bool(real["rain"]),
            }
        )

    db.commit()
    return {"items": items}

