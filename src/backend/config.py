"""Configuration loaded from .env"""
import os
from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_lnp_index")
