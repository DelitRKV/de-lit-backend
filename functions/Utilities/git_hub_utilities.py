from .utils import GITHUB_TOKEN, REPO_OWNER, REPO_NAME, FOLDER_PATH
import httpx
import datetime
import base64
from fastapi import HTTPException
import re

async def upload_to_github(file_content, file_name):
    """ Uploading the actual image file into GitHub repository
    
    Args:
        file_content (bytes): actual file content (binary data)
        file_name (str): name of the file
    
    Returns:
        object: httpx.Response object
    """
    # Ensure the file content is in bytes (for binary files)
    if not isinstance(file_content, bytes):
        raise ValueError("file_content must be in binary format")

    # GitHub API URL
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FOLDER_PATH}/{file_name}"

    # Prepare headers
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get current time for commit message
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Base64 encode the file content (binary data)
    encoded_content = base64.b64encode(file_content).decode("utf-8")
    
    # Data to be sent in the API request
    data = {
        "message": f"Add {file_name} at {now}",
        "content": encoded_content
    }

    # Send the PUT request to GitHub API
    async with httpx.AsyncClient() as client:
        response = await client.put(url, json=data, headers=headers)
    
    

    
    return response

async def delete_file_from_github(link: str):
    """Delete the file from a GitHub repository.

    Args:
        link (str): Raw file link in the form of `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<file_path>`.

    Raises:
        HTTPException: If the link is invalid or the file cannot be deleted.

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
    # Debug extracted values
    print(f"Repository Owner: {REPO_OWNER}")
    print(f"Repository Name: {REPO_NAME}")
    print(f"Branch: {BRANCH}")
    print(f"File Path: {file_path}")

    # GitHub API URL to get the file content metadata
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}?ref={BRANCH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",  # Replace with your GitHub token
        "Accept": "application/vnd.github.v3+json"
    }

    # Get the SHA of the file to delete
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
    if response.status_code != 200:
        raise HTTPException(
            status_code=404, detail="File not found in the repository"
        )

    sha = response.json().get("sha")
    if not sha:
        raise HTTPException(
            status_code=400, detail="Unable to retrieve file SHA"
        )

    # Prepare the payload to delete the file
    delete_payload = {
        "message": f"Delete {file_path}",
        "sha": sha
    }
    
    # Delete the file from GitHub
    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers, params=delete_payload)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code, detail="Failed to delete the file"
        )

    return response