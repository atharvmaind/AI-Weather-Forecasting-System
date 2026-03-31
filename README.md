## AI Weather Forecasting System (10-Day Prediction)

Full-stack ML weather forecasting project with a modern dashboard UI.

### Features

- **Predict weather for next N days (1–10)**  
- **Rainy / Not Rainy prediction** (RandomForestClassifier)
- **Temperature prediction** (RandomForestRegressor)
- **Humidity prediction** (RandomForestRegressor)
- **Real weather integration** via Open-Meteo (city + start date)
- **Real vs Predicted comparison** (cards + charts)
- **Past 7 days weather** from database
- **Charts & graphs** (Recharts) + animated UI
- **Stores predictions in a database** (SQLAlchemy: SQLite locally, PostgreSQL in production)
- **REST API backend** (FastAPI)
- **Deployment-ready**: Backend on Render, Frontend on Vercel

### Tech Stack

- **Frontend**: React, Tailwind CSS, Axios, Recharts
- **Backend**: FastAPI, Pandas, NumPy, Scikit-learn, SQLAlchemy
- **Database**: PostgreSQL (production) or **SQLite** (local default, no install)

### Project Structure

```text
frontend/
backend/
models/
data/
requirements.txt
README.md
```

### Installation

#### 1) Database (local vs production)

- **Local (default):** no setup. The API uses **SQLite** at `data/weather.db` when `DATABASE_URL` is not set.
- **PostgreSQL:** if you set `DATABASE_URL` in `backend/.env`, PostgreSQL must be running and reachable. If you see `connection refused` on port 5432, either start PostgreSQL or **remove** `DATABASE_URL` from `.env` to use SQLite.

Example PostgreSQL URL:

- `postgresql+psycopg2://postgres:postgres@localhost:5432/weatherdb`

#### 2) Backend setup

From project root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Optional env file:

- Copy `backend/.env.example` → `backend/.env`
- Set `DATABASE_URL` only when using PostgreSQL (Render/production, or local Postgres)

Generate a bigger sample dataset (optional but recommended):

```bash
python data/generate_dataset.py
```

Run the backend:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

#### 3) Frontend setup

```bash
cd frontend
npm install
```

Set API URL:

- Copy `frontend/.env.example` → `frontend/.env`
- Set `VITE_API_URL=http://localhost:8000`

Run the frontend:

```bash
npm run dev
```

Open the app at `http://localhost:5173`.

### API Endpoints
- **GET** `/real-weather?city=Pune&start_date=YYYY-MM-DD&days=7`
  Returns real daily weather from Open-Meteo.
- **GET** `/past-weather`  
  Returns last 7 days weather from `weather_data`.

- **POST** `/train-model`  
  Loads `data/weather.csv` into DB and trains ML models into `models/`.

- **POST** `/predict`  
  Body:

```json
{
  "city": "Pune",
  "start_date": "2026-04-01",
  "days": 10
}
```

Fetches real weather (Open-Meteo), runs ML predictions, returns combined results, and stores predictions in `predictions`.

### Database Tables

#### `weather_data`

- `id`
- `date`
- `temperature`
- `humidity`
- `rain`

*(Implementation also includes `pressure` and `wind_speed` for better ML features.)*

#### `predictions`

- `id`
- `date`
- `predicted_temp`
- `predicted_humidity`
- `rain_prediction`
- `rain_probability`

### Deployment

#### Backend → Render

- Set env var **DATABASE_URL**
- Start command:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

#### Frontend → Vercel

- Framework: **Vite**
- Build command: `npm run build`
- Output: `dist`
- Env var: **VITE_API_URL** = your Render backend URL

### Screenshots

- Add screenshots to a `screenshots/` folder and reference them here.

