from fastapi import HTTPException
from functools import wraps



GITHUB_TOKEN = ""
REPO_OWNER = "Harshad712"
REPO_NAME = "RKV-SPORTS-TEST"
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


