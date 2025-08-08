from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

def get_engine(db_key):
    url = os.getenv(db_key)
    if url is None:
        raise ValueError(f"Environment variable '{db_key}' is not set")
    return create_engine(url)