# Standard Libraries
import pickle
import logging

# Third-Party Libraries
import pandas as pd
from sigfig import round
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from enum import Enum
from babel.numbers import format_currency
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Rate Limiting Libraries
from fastapi import Request
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler

# Local Modules
from api.config import settings

# Logging the Output
logging.basicConfig(level=logging.INFO, format="%(levelname)s:    %(message)s")
logger = logging.getLogger(__name__)

# Loading Pipeline and Model Frequency
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with open(settings.PIPE_PATH, "rb") as f:
            app.state.pipe = pickle.load(f)
            logger.info("Pipeline loaded successfully")
        with open(settings.MODEL_FREQ_PATH, "rb") as f:
            app.state.model_freq = pickle.load(f)
            logger.info("Model frequency loaded successfully")
    except Exception:
        logger.exception("Model loading failed")
    
    yield

# Creating FastAPI App Instance
app = FastAPI(title="AutoIQ by Motor.co", lifespan=lifespan)

# Setting up Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS so frontend apps from different origins can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/", tags=["General"])
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Pipeline is live"}

# Health Check Endpoint
@app.get("/health", tags=["Utility"])
def health():
    logger.info("Health endpoint accessed")
    return {
        "status": "ok",
        "pipeline_loaded": app.state.pipe is not None,
        "model_frequency_loaded": app.state.model_freq is not None
    }

# Input validation for fuel_type
class FuelType(str, Enum):
    PETROL = "Petrol"
    DIESEL = "Diesel"
    CNG = "CNG"

# Input validation for transmission
class Transmission(str, Enum):
    MANUAL = "Manual"
    AUTOMATIC = "Automatic"

# Input validation for owner
class OwnerType(str, Enum):
    FIRST = "1st owner"
    SECOND = "2nd owner"
    THIRD = "3rd owner"
    OTHERS = "Others"

# Define Input Data Schema using Pydantic
class Input(BaseModel):
    brand: str = Field(..., description="Brand Name of your Car", example="MG")
    model: str = Field(..., description="Model Name of your Car", example="HECTOR")  
    km_driven: int = Field(..., ge=1000, le=200000, description="KM Driven of your Car", example=80000)
    engine_capacity: int = Field(..., ge=700, le=3000, description="Engine Capacity (in cc) of your Car", example=1498)
    fuel_type: FuelType = Field(..., description="Fuel Type of your Car", example="Petrol")
    transmission: Transmission = Field(..., description="Transmission of your Car", example="Manual")
    year: int = Field(..., ge=2010, le=2024, description="Manufacture Year of your Car", example=2022)
    owner: OwnerType = Field(..., description="Owner Type of your Car", example="1st owner")

# Prediction Endpoint
@app.post("/predict", tags=["Prediction"])
@limiter.limit("10/minute")
def predict(data: Input, request: Request):
    pipe = request.app.state.pipe
    model_freq = request.app.state.model_freq

    # Check if Models are Loaded
    if pipe is None:
        logger.error("Pipeline is not loaded")
        return {"error": "Pipeline is not available"}
    if model_freq is None:
        logger.error("Model frequency is not loaded")
        return {"error": "Model frequency is not available"}

    try:
        input_data = pd.DataFrame({
                        "brand":[data.brand],
                        "model_freq":[model_freq.get(data.model)],
                        "km_driven":[data.km_driven],
                        "engine_capacity":[data.engine_capacity],
                        "fuel_type":[data.fuel_type],
                        "transmission":[data.transmission],
                        "year":[data.year],
                        "owner":[data.owner]
                        })
        logger.info("Input data prepared for prediction")
        
        prediction = round(pipe.predict(input_data)[0])
        logger.info("Prediction made successfully")

        lower_limit = prediction - settings.MAE
        upper_limit = prediction + settings.MAE

        format_lower = format_currency(round(lower_limit,3), "INR", locale="en_IN")
        format_upper = format_currency(round(upper_limit,3), "INR", locale="en_IN")

        result = f"{format_lower.split('.')[0]} to {format_upper.split('.')[0]}"
        logger.info("Prediction formatted successfully")
        return {"output": result}
    except Exception:
        logger.exception("Prediction failed due to an exception")
        return {"error": "An unexpected error occurred during prediction"}