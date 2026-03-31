from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    # Run as package: uvicorn backend.app:app (from project root)
    from .database import Base, engine
    from .routes import router as api_router
except ImportError:  # pragma: no cover
    # Run from backend folder: uvicorn app:app
    from database import Base, engine  # type: ignore
    from routes import router as api_router  # type: ignore


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Weather Forecasting System (10-Day Prediction)",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root():
        return {
            "service": "AI Weather Forecasting API",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "endpoints": {
                "past_weather": {"method": "GET", "path": "/past-weather"},
                "train_model": {"method": "POST", "path": "/train-model"},
                "predict": {"method": "POST", "path": "/predict", "body": {"days": "1-10"}},
            },
            "hint": "Open /docs for interactive API. Use the React app on port 5173 for the dashboard.",
        }

    @app.get("/health")
    def health():
        return {"status": "ok"}

    Base.metadata.create_all(bind=engine)
    app.include_router(api_router)
    return app


app = create_app()
