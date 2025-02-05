from fastapi import HTTPException
from functools import wraps
from dotenv import load_dotenv
import os
import json
import re
from firebase_functions import  options
'''
load_dotenv()

firebase_config = os.getenv('FIREBASE_CONFIG')
    

# Parse the Firebase Config JSON
firebase_config = json.loads(firebase_config)
        
# Access the specific keys
github_token = firebase_config.get('github', {}).get('token') '''
    
GITHUB_TOKEN = ""
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


def is_url(string):
    # Basic pattern for validating a URL
    url_pattern = re.compile(r'https?://(?:www\.)?.+\..+')
    return bool(url_pattern.match(string))

def is_github_link(url):
    """Check if the URL is a GitHub link."""
    return "raw.githubusercontent.com" in url



# Global CORS configuration allowing all origins and methods
cors_config = options.CorsOptions(
    cors_origins=["*"],  # Allow all origins
    cors_methods=["*"],  # Allow all HTTP methods
    
)


