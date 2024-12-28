from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception

crud_repo = CrudRepository(collection_name="Home")

@handle_exception
@https_fn.on_request()
def create_block(request):
  
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Parse the form data
        block_title = request.form.get("block_title")
        block_image = request.files.get("block_image")
        other_data = {key: value for key, value in request.form.items() if key not in ["block_title", "block_image"]}

        # Validate inputs
        if not block_title:
            return {"error": "block title is required"}, 400

        

        # Upload the profile image (if provided)
        block_image_link = None
        if block_image:
            block_image_link = crud_repo.upload_image(block_image)
            if not block_image_link:
                return {"error": "Failed to upload profile image to GitHub"}, 500

        # Combine all data
        data = {"block_title": block_title, "block_image_link": block_image_link, **other_data}

        # Create the block in Firestore
        result = crud_repo.create(data)
        return {"message": "block created successfully", "result": result}, 201

   
@handle_exception
@https_fn.on_request()
def update_block(request):
    
        # Validate Content-Type for multipart/form-data
        if "multipart/form-data" not in request.headers.get("Content-Type", ""):
            return {"error": "Unsupported Media Type. Use 'multipart/form-data' for file uploads."}, 415

        # Extract text data and file from the request
        block_title = request.form.get("block_title")
        block_id = request.form.get("id")
        block_image = request.files.get("block_image")  # Extracting image file
        
        # Extract other fields dynamically
        other_fields = {key: value for key, value in request.form.items() if key not in ["block_title", "id", "block_image"]}

        # Check for required fields
        if not block_id:
            return {"error": "Missing required fields: block_title or id"}, 400

        # Fields to be updated (initially with block_title)
        fields_to_update = {"block_title": block_title}

        # Add other fields to update (besides block_title and block_image)
        fields_to_update.update(other_fields)

        # Handle profile image update
        if block_image:
            # Extract current block details
            block = crud_repo.find_by({"id": block_id})
            if block:
                old_block_image_link = block.get("block_image_link")

                # Delete the old profile image from GitHub if it exists
                if old_block_image_link:
                    cover_image_delete = crud_repo.delete_link(old_block_image_link)
                    if not cover_image_delete:
                        return {"error": "Failed to delete the old profile image from GitHub"}, 500

                # Upload the new profile image to GitHub
                new_image_link = crud_repo.upload_image(block_image)
                if not new_image_link:
                    return {"error": "Failed to upload new profile image to GitHub"}, 500
                
                # Add new profile image link to fields_to_update
                fields_to_update["block_image_link"] = new_image_link

        # Update the block details
        result = crud_repo.update(block_id, fields_to_update)
        if not result:
            return {"error": f"block with id '{block_id}' not found"}, 404

        return {"message": "block updated successfully", "result": result}, 200

@handle_exception
@https_fn.on_request()
def delete_block(request):
   
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the ID of the block to delete
        block_id = data.get("id")

        # Find the block by ID to retrieve the profile image link
        block = crud_repo.find_by({"id": block_id})
        if not block:
            return {"error": "block not found"}, 404

        block_image_link = block.get("block_image_link")

        # If there is a profile image, delete it from GitHub
        if block_image_link:
            cover_image_delete = crud_repo.delete_link(block_image_link)
            if not cover_image_delete:
                return {"error": "Failed to delete the profile image from GitHub"}, 500

        # Delete the block using the CRUD repository
        result = crud_repo.delete(block_id)
        if not result:
            return {"error": "Failed to delete block"}, 500

        return {"message": "block and profile image deleted successfully"}, 200

    

@handle_exception
@https_fn.on_request()
def get_all_blocks(request):
    
        # Fetch all blocks using the CRUD repository
        blocks = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not blocks:
            return {"message": "No blocks found"}, 404

        return {"message": "blocks retrieved successfully", "blocks": blocks}, 200

    

@handle_exception
@https_fn.on_request()
def get_block_by_id(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the block block_title from the request
        block_id = data.get("id")
        if not block_id:
            return {"error": "Missing required field: block_id"}, 400

        # Fetch the block by block_title using the CRUD repository
        block = crud_repo.find_by({"id": block_id})
        if not block:
            return {"error": f"block with block_id '{block_id}' not found"}, 404

        return {"message": "block retrieved successfully", "block": block}, 200

   


