from fastapi import HTTPException, UploadFile
from google.cloud import firestore
from google.oauth2 import service_account
from typing import TypeVar, Generic, Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from Utilities.git_hub_utilities import upload_to_github, delete_file_from_github
from Utilities.utils import REPO_OWNER, REPO_NAME, BRANCH
import os
import random


#service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#credentials = service_account.Credentials.from_service_account_file(service_account_path)
project_id = "de-lit-web"


T = TypeVar('T', bound=BaseModel)

class CrudRepository(Generic[T]):
    def __init__(self, collection_name: str):
        
        self.db = firestore.Client(project=project_id)
        self.collection = self.db.collection(collection_name)
        self.collection_name = collection_name

    def create(self, data: T) -> T:
        try:
            document = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data
            doc_ref = self.collection.document()
            document['id'] = doc_ref.id
            document['created_at'] = datetime.now()
            doc_ref.set(document)
            return data.model_validate(document) if hasattr(data, 'model_validate') else document
        except Exception as error:
            print(f"Error creating document: {error}")
            raise HTTPException(status_code=400, detail=f"Failed to create the document: {str(error)}") from error

    def delete(self, id: str) -> Optional[T]:
        doc_ref = self.collection.document(id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_ref.delete()
        return {"message": "Document deleted successfully"}
    def delete_all(self) -> Optional[T]:
        docs = self.collection.stream()  # Get all documents
        deleted_count = 0

        for doc in docs:
            doc.delete()  # Delete each document
            deleted_count += 1

        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="No documents found")

        return {"message": f"{deleted_count} documents deleted successfully"}

    def get(self, id: str) -> Optional[T]:
        doc = self.collection.document(id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc.to_dict()

    def find_by(self, query: Dict) -> Optional[T]:
        if len(query) == 1:
            # Using the first key-value pair for the query
            field, value = list(query.items())[0]
            docs = self.collection.where(field, "==", value).stream()

            # Return the first matching document as a dictionary, if any
            for doc in docs:
                return doc.to_dict()  # Return the first document found
        else:
            # Handle more complex queries if needed (optional)
            raise NotImplementedError("Multiple conditions query is not supported yet.")
        
        # If no document is found
        return None

    def get_all(self) -> List[T]:
        docs = self.collection.stream()
        return [doc.to_dict() for doc in docs]

    def update(self, id: str, data: T) -> Optional[T]:
        doc_ref = self.collection.document(id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Document not found")
        document = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data
        doc_ref.update(document)
        return {"message": "Document updated successfully"}

    def upload_image(self, file:UploadFile):
        if file:
            file_content =  file.stream.read()
            image_size = len(file_content)

            max_length = 10 * 1024 * 1024  # 10 MB limit
            if image_size > max_length:
                raise HTTPException(status_code=413, detail="File size exceeds the limit of 10 MB.")

            file.stream.seek(0)
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            # Modify the filename to include timestamp
            file_name_with_timestamp = f"{timestamp}_{random.random()}_{file.filename}"
            
            
            response =upload_to_github(file_content, file_name_with_timestamp,self.collection_name)
            
            

            if response.status_code == 201:
                file_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{self.collection_name}/{file_name_with_timestamp}"
            else:
                raise HTTPException(status_code=400, detail="Error uploading file to GitHub")

            return file_url

    def delete_link(self, image_url: str):
        response = delete_file_from_github(image_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=409,
                detail="Conflict: Unable to delete the image from GitHub"
            )
        return {"message": "Image successfully deleted from GitHub"}
