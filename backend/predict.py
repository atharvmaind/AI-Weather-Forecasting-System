from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

try:
    from .ml_utils import LastKnown, make_future_features
except ImportError:  # pragma: no cover
    from ml_utils import LastKnown, make_future_features  # type: ignore


MODELS_DIR = Path(__file__).resolve().parents[1] / "models"


@dataclass
class ForecastItem:
    date: date
    predicted_temp: float
    predicted_humidity: float
    rain_prediction: bool
    rain_probability: float


def _load_models():
    rain = joblib.load(MODELS_DIR / "rain_model.pkl")
    temp = joblib.load(MODELS_DIR / "temp_model.pkl")
    hum = joblib.load(MODELS_DIR / "humidity_model.pkl")
    return rain, temp, hum


def forecast_next_n(last_known: LastKnown, days: int) -> list[ForecastItem]:
    rain_model, temp_model, hum_model = _load_models()

    future_dates = [last_known.last_date + timedelta(days=i) for i in range(1, days + 1)]
    x = make_future_features(last_known, future_dates)

    proba = rain_model.predict_proba(x)[:, 1]
    rain_pred = (proba >= 0.5).astype(int)
    temp_pred = temp_model.predict(x)
    hum_pred = hum_model.predict(x)

    out: list[ForecastItem] = []
    for i, d in enumerate(future_dates):
        out.append(
            ForecastItem(
                date=d,
                predicted_temp=float(np.round(temp_pred[i], 2)),
                predicted_humidity=float(np.round(hum_pred[i], 2)),
                rain_prediction=bool(int(rain_pred[i])),
                rain_probability=float(np.round(proba[i], 4)),
            )
        )
    return out


def predict_from_features(x: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns (pred_temp, pred_humidity, rain_proba_1) for a given feature matrix.
    """
    rain_model, temp_model, hum_model = _load_models()
    rain_proba = rain_model.predict_proba(x)[:, 1]
    temp_pred = temp_model.predict(x)
    hum_pred = hum_model.predict(x)
    return temp_pred, hum_pred, rain_proba
