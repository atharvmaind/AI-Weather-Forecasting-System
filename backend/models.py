from sqlalchemy import Boolean, Column, Date, Float, Integer

try:
    from .database import Base
except ImportError:  # pragma: no cover
    from database import Base  # type: ignore


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    rain = Column(Boolean, nullable=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    predicted_temp = Column(Float, nullable=False)
    predicted_humidity = Column(Float, nullable=False)
    rain_prediction = Column(Boolean, nullable=False)
    rain_probability = Column(Float, nullable=False)
