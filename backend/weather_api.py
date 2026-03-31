from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests


@dataclass(frozen=True)
class RealWeatherDay:
    date: dt.date
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    rain: bool
    rain_probability: float  # 0..1
    weather_icon: str  # "Sunny" | "Cloudy" | "Rainy"


def _geocode_city(city: str) -> tuple[float, float]:
    # Open-Meteo geocoding (no API key)
    url = "https://geocoding-api.open-meteo.com/v1/search"
    resp = requests.get(url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        raise ValueError(f"Could not geocode city: {city}")
    first = results[0]
    return float(first["latitude"]), float(first["longitude"])


def _hourly_to_daily(hourly: dict[str, Any]) -> list[RealWeatherDay]:
    # hourly arrays are aligned by index; Open-Meteo returns:
    # hourly.time (list of ISO strings) and one list per variable.
    times = hourly.get("time") or []
    if not times:
        return []

    df = pd.DataFrame({"time": pd.to_datetime(times, utc=True)})
    df["date"] = df["time"].dt.date

    var_map = {
        "temperature_2m": "temperature",
        "relative_humidity_2m": "humidity",
        "pressure_msl": "pressure",
        "wind_speed_10m": "wind_speed",
        "rain": "rain_amount",
        "precipitation_probability": "precip_probability",
        "weather_code": "weather_code",
    }

    for open_var, col in var_map.items():
        vals = hourly.get(open_var)
        if vals is None:
            # If a variable is missing, fill zeros so model input can proceed.
            df[col] = 0.0
        else:
            df[col] = vals

    grouped = df.groupby("date", as_index=False)

    out: list[RealWeatherDay] = []
    for _, g in grouped:
        temperature = float(g["temperature"].mean())
        humidity = float(g["humidity"].mean())
        pressure = float(g["pressure"].mean())
        wind_speed = float(g["wind_speed"].mean())

        rain_sum = float(g["rain_amount"].sum())
        rain = rain_sum > 0.1  # mm per day threshold-ish

        precip_prob_mean = float(g["precip_probability"].mean())
        rain_probability = max(0.0, min(1.0, precip_prob_mean / 100.0))

        # icon mapping (simple + robust)
        weather_code = int(round(float(g["weather_code"].mode().iloc[0]))) if len(g["weather_code"].mode()) else 0
        if rain:
            icon = "Rainy"
        elif weather_code in (0, 1, 2):
            icon = "Sunny"
        else:
            icon = "Cloudy"

        out.append(
            RealWeatherDay(
                date=dt.date.fromisoformat(str(g["date"].iloc[0])),
                temperature=temperature,
                humidity=humidity,
                pressure=pressure,
                wind_speed=wind_speed,
                rain=rain,
                rain_probability=rain_probability,
                weather_icon=icon,
            )
        )

    out.sort(key=lambda x: x.date)
    return out


def fetch_real_weather(city: str, start_date: str, days: int) -> list[dict[str, Any]]:
    """
    Fetch real weather from Open-Meteo and return daily aggregates.

    Returns a list of dicts:
      {
        "date": "YYYY-MM-DD",
        "temperature": float,
        "humidity": float,
        "pressure": float,
        "wind_speed": float,
        "rain": bool,
        "rain_probability": float(0..1),
        "weather_icon": "Sunny"|"Cloudy"|"Rainy"
      }
    """
    if days < 1 or days > 30:
        raise ValueError("days must be between 1 and 30 for Open-Meteo calls")

    lat, lon = _geocode_city(city)

    start = dt.date.fromisoformat(start_date)
    end = start + dt.timedelta(days=days - 1)

    # Use hourly variables then aggregate to daily for consistency with the ML lag feature.
    # Note: parameter names are Open-Meteo standard.
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "rain",
                "wind_speed_10m",
                "pressure_msl",
                "weather_code",
            ]
        ),
        "timezone": "UTC",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
    }

    url = "https://api.open-meteo.com/v1/forecast"
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    hourly = data.get("hourly") or {}
    daily = _hourly_to_daily(hourly)

    # Ensure we return exactly `days` results when possible.
    daily_by_date = {x.date: x for x in daily}
    out: list[dict[str, Any]] = []
    for i in range(days):
        d = start + dt.timedelta(days=i)
        if d not in daily_by_date:
            # fallback defaults if a day is missing for any reason
            out.append(
                {
                    "date": d.isoformat(),
                    "temperature": 0.0,
                    "humidity": 0.0,
                    "pressure": 0.0,
                    "wind_speed": 0.0,
                    "rain": False,
                    "rain_probability": 0.0,
                    "weather_icon": "Cloudy",
                }
            )
            continue

        x = daily_by_date[d]
        out.append(
            {
                "date": x.date.isoformat(),
                "temperature": x.temperature,
                "humidity": x.humidity,
                "pressure": x.pressure,
                "wind_speed": x.wind_speed,
                "rain": x.rain,
                "rain_probability": x.rain_probability,
                "weather_icon": x.weather_icon,
            }
        )

    return out


def fetch_past_weather(city: str, start_date: str, days: int = 7) -> list[dict[str, Any]]:
    """
    Fetch previous `days` days (historical) ending at start_date-1 using Open-Meteo Archive API.

    Returns list:
      { "date": "YYYY-MM-DD", "temperature": float, "humidity": float, "rain": "Yes"|"No" }
    """
    if days < 1 or days > 14:
        raise ValueError("days must be between 1 and 14 for past-weather")

    lat, lon = _geocode_city(city)
    start = dt.date.fromisoformat(start_date)
    end_hist = start - dt.timedelta(days=1)
    start_hist = end_hist - dt.timedelta(days=days - 1)

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "rain",
            ]
        ),
        "timezone": "UTC",
        "start_date": start_hist.isoformat(),
        "end_date": end_hist.isoformat(),
    }

    url = "https://archive-api.open-meteo.com/v1/archive"
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    hourly = data.get("hourly") or {}

    times = hourly.get("time") or []
    if not times:
        return []

    df = pd.DataFrame({"time": pd.to_datetime(times, utc=True)})
    df["date"] = df["time"].dt.date
    df["temperature"] = hourly.get("temperature_2m") or [0.0] * len(df)
    df["humidity"] = hourly.get("relative_humidity_2m") or [0.0] * len(df)
    df["rain_amount"] = hourly.get("rain") or [0.0] * len(df)

    out: list[dict[str, Any]] = []
    for d, g in df.groupby("date"):
        rain_sum = float(pd.Series(g["rain_amount"]).sum())
        out.append(
            {
                "date": d.isoformat(),
                "temperature": float(pd.Series(g["temperature"]).mean()),
                "humidity": float(pd.Series(g["humidity"]).mean()),
                "rain": "Yes" if rain_sum > 0.1 else "No",
            }
        )

    out.sort(key=lambda x: x["date"])
    # Ensure exactly `days` items where possible
    return out[-days:]

