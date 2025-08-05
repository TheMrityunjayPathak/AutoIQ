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