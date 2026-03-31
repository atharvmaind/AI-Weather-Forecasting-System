from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd


def _date_features(d: pd.Series) -> pd.DataFrame:
    doy = d.dt.dayofyear.astype(int)
    dow = d.dt.dayofweek.astype(int)
    return pd.DataFrame(
        {
            "day_of_year": doy,
            "day_of_week": dow,
            "sin_doy": np.sin(2 * np.pi * doy / 365.25),
            "cos_doy": np.cos(2 * np.pi * doy / 365.25),
        }
    )


def make_supervised(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series, pd.Series]:
    """
    Create a supervised dataset using lag features.
    Predict (temp, humidity, rain) of day t using features of day t-1 plus date features.
    """
    df = df.sort_values("date").reset_index(drop=True).copy()
    df["date"] = pd.to_datetime(df["date"])

    shifted = df.shift(1)
    shifted.columns = [f"lag1_{c}" for c in shifted.columns]
    feat = pd.concat([df[["date"]], shifted], axis=1).dropna().reset_index(drop=True)

    date_feat = _date_features(feat["date"])
    x = pd.concat(
        [
            date_feat,
            feat[
                [
                    "lag1_temperature",
                    "lag1_humidity",
                    "lag1_pressure",
                    "lag1_wind_speed",
                    "lag1_rain",
                ]
            ].astype(float),
        ],
        axis=1,
    )

    y_temp = df.loc[1:, "temperature"].reset_index(drop=True)
    y_hum = df.loc[1:, "humidity"].reset_index(drop=True)
    y_rain = df.loc[1:, "rain"].astype(int).reset_index(drop=True)
    return x, y_rain, y_temp, y_hum


@dataclass
class LastKnown:
    last_date: date
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    rain: int


def make_future_features(last_known: LastKnown, future_dates: list[date]) -> pd.DataFrame:
    d = pd.to_datetime(pd.Series(future_dates))
    date_feat = _date_features(d)

    x = pd.concat(
        [
            date_feat,
            pd.DataFrame(
                {
                    "lag1_temperature": [last_known.temperature] * len(future_dates),
                    "lag1_humidity": [last_known.humidity] * len(future_dates),
                    "lag1_pressure": [last_known.pressure] * len(future_dates),
                    "lag1_wind_speed": [last_known.wind_speed] * len(future_dates),
                    "lag1_rain": [float(last_known.rain)] * len(future_dates),
                }
            ),
        ],
        axis=1,
    )
    return x


def make_target_features(target_dates: list[date], prev_rows: list[LastKnown]) -> pd.DataFrame:
    """
    Build model features for each `target_date` using the corresponding `prev_rows[i]` (lag-1 values).
    """
    if len(target_dates) != len(prev_rows):
        raise ValueError("target_dates and prev_rows must have the same length")

    d = pd.to_datetime(pd.Series(target_dates))
    date_feat = _date_features(d)

    lag_df = pd.DataFrame(
        {
            "lag1_temperature": [r.temperature for r in prev_rows],
            "lag1_humidity": [r.humidity for r in prev_rows],
            "lag1_pressure": [r.pressure for r in prev_rows],
            "lag1_wind_speed": [r.wind_speed for r in prev_rows],
            "lag1_rain": [float(r.rain) for r in prev_rows],
        }
    )
    x = pd.concat([date_feat.reset_index(drop=True), lag_df.reset_index(drop=True)], axis=1)
    return x
