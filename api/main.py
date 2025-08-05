# Standard Libraries
import pickle
import logging

# Third-Party Libraries
import pandas as pd
from sigfig import round
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
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