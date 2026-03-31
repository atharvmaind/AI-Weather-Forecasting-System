from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

try:
    # When executed as a module: python -m backend.train
    from .ml_utils import make_supervised
except ImportError:  # pragma: no cover
    # When executed as a script from the backend/ folder: python train.py
    from ml_utils import make_supervised  # type: ignore


MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train_from_csv(csv_path: str) -> dict:
    df = pd.read_csv(csv_path)
    required = {"date", "temperature", "humidity", "pressure", "wind_speed", "rain"}
    missing = required - set(df.columns.str.lower())
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")

    # normalize columns
    df.columns = [c.lower() for c in df.columns]
    df["rain"] = df["rain"].astype(int)

    x, y_rain, y_temp, y_hum = make_supervised(df)

    rain_clf = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    temp_reg = RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        n_jobs=-1,
    )
    hum_reg = RandomForestRegressor(
        n_estimators=400,
        random_state=42,
        n_jobs=-1,
    )

    rain_clf.fit(x, y_rain)
    temp_reg.fit(x, y_temp)
    hum_reg.fit(x, y_hum)

    joblib.dump(rain_clf, MODELS_DIR / "rain_model.pkl")
    joblib.dump(temp_reg, MODELS_DIR / "temp_model.pkl")
    joblib.dump(hum_reg, MODELS_DIR / "humidity_model.pkl")

    return {"trained": True, "rows": int(len(df))}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    csv_path = root / "data" / "weather.csv"
    result = train_from_csv(str(csv_path))
    print(f"Trained models from {csv_path} (rows={result['rows']}). Saved to {MODELS_DIR}.")
