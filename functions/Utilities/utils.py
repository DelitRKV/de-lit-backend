from fastapi import HTTPException
from functools import wraps
from dotenv import load_dotenv
import os
import json

load_dotenv()



GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "DelitRKV"
REPO_NAME = "de-lit-media"
BRANCH = "main"

firebase_config = os.getenv("FIREBASE_CONFIG")

# Parse JSON config if it's in a string format
if firebase_config:
    config = json.loads(firebase_config)
    
    # Access nested dictionary values
    #GITHUB_TOKEN = config.get("github", {}).get("token")


def handle_exception(function):
    @wraps(function)
    def wrapper(*arguments, **kwargs):
        try:
            return function(*arguments, **kwargs)
        except HTTPException as http_exce:
            raise http_exce
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"An unknown error occurred.{str(e)}"
            )

    return wrapper


