from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository

crud_repo = CrudRepository(collection_name="Gallery")

@https_fn.on_request()
def create_memory(request):
    try:
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

    except Exception as e:
        # Log error for debugging (optional)
        print(f"Error occurred: {e}")
        return {"error": f"Internal Server Error: {str(e)}"}, 500

@https_fn.on_request()
def delete_memory(request):
    try:
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "Request body is required"}, 400

        # Retrieve the image link and Firestore document ID
        image_link = data.get("image_link")
        document_id = data.get("id")

        if not image_link or not document_id:
            return {"error": "'image_link' and 'document_id' are required"}, 400

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

    except Exception as e:
        # Log error for debugging (optional)
        print(f"Error occurred: {e}")
        return {"error": f"Internal Server Error: {str(e)}"}, 500
