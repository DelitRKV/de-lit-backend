from fastapi import HTTPException
from functools import wraps
from dotenv import load_dotenv
import os
import json

load_dotenv()

firebase_config = os.getenv('FIREBASE_CONFIG')
    

# Parse the Firebase Config JSON
firebase_config = json.loads(firebase_config)
        
# Access the specific keys
github_token = firebase_config.get('github', {}).get('token')
    
GITHUB_TOKEN = github_token
       







REPO_OWNER = "DelitRKV"
REPO_NAME = "de-lit-media"
BRANCH = "main"



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


