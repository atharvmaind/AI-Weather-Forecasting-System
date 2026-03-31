from datetime import date
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    city: str = Field(min_length=1, max_length=120, description="City name (e.g. Pune)")
    start_date: date = Field(description="Start date for forecasting (YYYY-MM-DD)")
    days: int = Field(ge=1, le=10, description="Number of days to forecast (1-10)")


class WeatherRow(BaseModel):
    date: date
    temperature: float
    humidity: float
    rain: bool


class PredictionRow(BaseModel):
    date: date
    predicted_temp: float
    predicted_humidity: float
    rain_prediction: bool
    rain_probability: float


class TrainResponse(BaseModel):
    rows_loaded: int
    trained: bool


class PastWeatherResponse(BaseModel):
    items: list[WeatherRow]


class RealWeatherRow(BaseModel):
    date: date
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    rain: bool
    rain_probability: float
    weather_icon: str


class RealWeatherResponse(BaseModel):
    items: list[RealWeatherRow]


class PredictCombinedRow(BaseModel):
    date: date
    real_temperature: float
    real_humidity: float
    predicted_temperature: float
    predicted_humidity: float
    real_weather_icon: str
    predicted_weather_icon: str
    rain_probability: float
    rain_prediction: str  # "Yes" | "No"
    real_rain: bool


class PredictResponse(BaseModel):
    items: list[PredictCombinedRow]
