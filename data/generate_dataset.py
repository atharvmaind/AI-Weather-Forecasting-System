from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class Config:
    start_date: date = date(2024, 1, 1)
    days: int = 730
    seed: int = 42
    out_path: Path = Path(__file__).resolve().parent / "weather.csv"


def main(cfg: Config) -> None:
    rng = np.random.default_rng(cfg.seed)
    dates = [cfg.start_date + timedelta(days=i) for i in range(cfg.days)]
    t = np.arange(cfg.days)

    # simple seasonality + noise (synthetic but realistic ranges)
    temp = 26 + 8 * np.sin(2 * np.pi * t / 365.25 + 0.6) + rng.normal(0, 1.2, cfg.days)
    humidity = 62 + 18 * np.sin(2 * np.pi * t / 365.25 - 0.9) + rng.normal(0, 3.0, cfg.days)
    pressure = 1012 + 4 * np.cos(2 * np.pi * t / 14.0) + rng.normal(0, 1.8, cfg.days)
    wind = 5.5 + 2.0 * np.sin(2 * np.pi * t / 10.0) + rng.normal(0, 0.8, cfg.days)

    humidity = np.clip(humidity, 20, 95)
    wind = np.clip(wind, 0, 20)

    # rain probability influenced by humidity + pressure
    logit = -6.0 + 0.08 * humidity - 0.02 * (pressure - 1012) + rng.normal(0, 0.25, cfg.days)
    p_rain = 1 / (1 + np.exp(-logit))
    rain = rng.uniform(0, 1, cfg.days) < p_rain

    df = pd.DataFrame(
        {
            "date": [d.isoformat() for d in dates],
            "temperature": np.round(temp, 2),
            "humidity": np.round(humidity, 2),
            "pressure": np.round(pressure, 2),
            "wind_speed": np.round(wind, 2),
            "rain": rain.astype(int),
        }
    )
    cfg.out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cfg.out_path, index=False)
    print(f"Wrote {len(df)} rows to {cfg.out_path}")


if __name__ == "__main__":
    main(Config())

