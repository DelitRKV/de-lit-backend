from fastapi import HTTPException, UploadFile
from google.cloud import firestore
from typing import TypeVar, Generic, Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from github_utilities import upload_to_github, delete_file_from_github
from utils import REPO_OWNER, REPO_NAME, FOLDER_PATH, BRANCH

T = TypeVar('T', bound=BaseModel)

class CrudRepository(Generic[T]):
    def __init__(self, collection_name: str):
        self.db = firestore.Client()
        self.collection = self.db.collection(collection_name)

    async def create(self, data: T) -> T:
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

    async def delete(self, id: str) -> Optional[T]:
        doc_ref = self.collection.document(id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Document not found")
        doc_ref.delete()
        return {"message": "Document deleted successfully"}

    async def get(self, id: str) -> Optional[T]:
        doc = self.collection.document(id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc.to_dict()

    async def find_by(self, query: Dict) -> Optional[T]:
        docs = self.collection.where(list(query.keys())[0], '==', list(query.values())[0]).stream()
        return [doc.to_dict() for doc in docs]

    async def get_all(self) -> List[T]:
        docs = self.collection.stream()
        return [doc.to_dict() for doc in docs]

    async def update(self, id: str, data: T) -> Optional[T]:
        doc_ref = self.collection.document(id)
        if not doc_ref.get().exists:
            raise HTTPException(status_code=404, detail="Document not found")
        document = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data
        doc_ref.update(document)
        return {"message": "Document updated successfully"}

    async def upload_image(self, file: UploadFile = None):
        if file:
            file_content = await file.read()
            image_size = len(file_content)

            max_length = 10 * 1024 * 1024  # 10 MB limit
            if image_size > max_length:
                raise HTTPException(status_code=413, detail="File size exceeds the limit of 10 MB.")

            await file.seek(0)
            file_content = await file.read()
            
            response = await upload_to_github(file_content, file.filename)

            if response.status_code == 201:
                file_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{FOLDER_PATH}/{file.filename}"
            else:
                raise HTTPException(status_code=400, detail="Error uploading file to GitHub")

            return file_url

    async def delete_image(self, image_url: str):
        response = await delete_file_from_github(image_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=409,
                detail="Conflict: Unable to delete the image from GitHub"
            )
        return {"message": "Image successfully deleted from GitHub"}
