from fastapi import HTTPException
from functools import wraps



GITHUB_TOKEN = ""
REPO_OWNER = "Harshad712"
REPO_NAME = "RKV-SPORTS-TEST"
FOLDER_PATH = "testing"
BRANCH = "main"



def handle_exception(function):
    @wraps(function)
    async def wrapper(*arguments, **kwargs):
        try:
            return await function(*arguments, **kwargs)
        except HTTPException as http_exce:
            raise http_exce
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"An unknown error occurred.{str(e)}"
            )

    return wrapper


