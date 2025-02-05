from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception,cors_config

crud_repo = CrudRepository(collection_name="Gallery")

@handle_exception
@https_fn.on_request(cors=cors_config)
def create_memory(request):
  
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Check if the request contains a file and description
        file = request.files.get("file")
        description = request.form.get("description")
        print("Files received:", request.files)
        print("Form data received:", request.form)

        if not file or not description:
            
            return {"error": "Both 'file' and 'description' are required"}, 400

        # Upload image and get the link
        image_link = crud_repo.upload_image(file)
        if not image_link:
            return {"error": "Failed to retrieve image link from GitHub"}, 500

        # Prepare data for Firestore
        data = {
            "image_link": image_link,
            "description": description
        }
        # Save the data to Firestore
        result = crud_repo.create(data)

        return {
            "message": "Image uploaded successfully",
            "github_link": image_link,
            "firestore_result": result,
        }, 201

    
@handle_exception
@https_fn.on_request(cors=cors_config)
def delete_memory(request):
    
        # Validate Content-Type
       
        # Retrieve the image link and Firestore document ID
        
        document_id = request.args.get("id")
        image = crud_repo.find_by({"id":id})

        if not image:
           return {"error": "image not found"}, 404
        image_link = image.get("image_link")
        # Delete the image from GitHub
        delete_response = crud_repo.delete_link(image_link)
        if not delete_response:
            return {"error": "Failed to delete the image from GitHub"}, 500

        # Delete the associated Firestore document
        delete_firestore_response = crud_repo.delete(document_id)
        if not delete_firestore_response:
            return {"error": "Failed to delete the document from Firestore"}, 500

        return {
            "message": "Image and associated memory deleted successfully",
            "github_response": delete_response,
            "firestore_response": delete_firestore_response,
        }, 200

   
