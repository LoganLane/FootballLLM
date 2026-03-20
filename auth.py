import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()
auth_key = os.getenv("AUTH_KEY")

def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key != auth_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_api_key