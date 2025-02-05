from .utils import GITHUB_TOKEN, REPO_OWNER, REPO_NAME
import httpx
import datetime
import base64
from fastapi import HTTPException
import re


def upload_to_github(file_content, file_name, folder_path):
    """ Uploading the actual image file into GitHub repository with timestamp in filename
    
    Args:
        file_content (bytes): actual file content (binary data)
        file_name (str): name of the file
        folder_path (str): GitHub folder path where the file should be uploaded
    
    Returns:
        httpx.Response: Response object from GitHub API
    """
    # Ensure the file content is in bytes
    if not isinstance(file_content, bytes):
        raise ValueError("file_content must be in binary format")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # GitHub API URL
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{folder_path}/{file_name}"

    # Prepare headers
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Commit message
    commit_message = f"Add {file_name} at {timestamp}"
    
    # Base64 encode the file content
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    
    # Data for the API request
    data = {
        "message": commit_message,
        "content": encoded_content
    }

    # Use a synchronous client since the rest of the code is not asynchronous
    response = httpx.put(url, json=data, headers=headers)
    return response


def delete_file_from_github(link: str):
    """Delete the file from a GitHub repository.

    Args:
        link (str): Raw file link in the form of `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<file_path>`.

    Returns:
        object: httpx.Response object.
    """
    # Extract information from the raw link
    pattern = r"https://raw.githubusercontent.com/([^/]+)/([^/]+)/([^/]+)/(.+)"
    match = re.match(pattern, link)
    if not match:
        raise HTTPException(
            status_code=400, detail="Invalid GitHub raw link format"
        )

    REPO_OWNER, REPO_NAME, BRANCH, file_path = match.groups()

    # GitHub API URL to get the file content metadata
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}?ref={BRANCH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Step 1: Get the file's metadata (to retrieve the SHA)
    with httpx.Client() as client:
        response = client.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=404, detail="File not found in the repository"
        )

    sha = response.json().get("sha")
    if not sha:
        raise HTTPException(
            status_code=400, detail="Unable to retrieve file SHA"
        )

    # Step 2: Delete the file
    delete_payload = {
        "message": f"Delete {file_path}",
        "sha": sha
    }
    with httpx.Client() as client:
        delete_response = client.delete(
            url,
            headers=headers,
            params=delete_payload  # This is now correctly passed as JSON
        )

    if delete_response.status_code != 200:
        raise HTTPException(
            status_code=delete_response.status_code,
            detail=f"Failed to delete the file: {delete_response.text}"
        )
    print(delete_response)

    return delete_response
