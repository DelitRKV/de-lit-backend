from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception
from Utilities.email_service import send_email_to_users


crud_repo = CrudRepository(collection_name="Publications")

@handle_exception
@https_fn.on_request()
def create_publication(request):
    
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Extract files and form data
        cover_image = request.files.get("cover_image")
        publication_file = request.files.get("publication_file")
        other_fields = {key: request.form.get(key) for key in request.form}

        if  not publication_file :
            return {"error": " publication_file is  required"}, 400

        publication_name = other_fields["publication_name"]
        
       
        

        # Upload files to GitHub and get the links
       
        publication_file_link = crud_repo.upload_image(publication_file)

        if  not publication_file_link:
            return {"error": "Failed to upload files to GitHub"}, 500

        # Prepare the data for Firestore
        if cover_image:
            cover_image_link = crud_repo.upload_image(cover_image)
            firestore_data = {
            "publication_name": publication_name,
            "cover_image_link": cover_image_link,
            "publication_file_link": publication_file_link,
             }
            firestore_data.update(other_fields)
            
        else:
            firestore_data = {
            "publication_name": publication_name,
            
            "publication_file_link": publication_file_link,
             }
            firestore_data.update(other_fields)
            
            
        # Include all other text fields

        # Create the publication in Firestore
        result = crud_repo.create(firestore_data)
        '''if result:
            send_email_to_users(publication_name)'''

        return {
            "message": "Publication created successfully",
            "publication_file_link": publication_file_link,
            "firestore_result": result,
        }, 201

   
@handle_exception
@https_fn.on_request()
def update_publication(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the publication_name and check if it's provided
        publication_name = data.get("publication_name")
        if not publication_name:
            return {"error": "Missing required field: publication_name"}, 400

        # Remove publication_name from the fields to update (so it's not updated itself)
        fields_to_update = {key: value for key, value in data.items() }

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
       
        id = data.get("id")
       
            

        # Update the publication using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"Publication with name '{publication_name}' not found"}, 404

        return {"message": "Publication updated successfully", "result": result}, 200


@handle_exception
@https_fn.on_request()
def delete_publication(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the ID of the publication to delete
        publication_id = data.get("id")
        if not publication_id:
            return {"error": "Publication ID is required"}, 400

        # Fetch the publication
        publication = crud_repo.find_by({"id": publication_id})
        if not publication:
            return {"error": "Publication not found"}, 404

        # Delete associated links if they exist
        cover_image_link = publication.get("cover_image_link")
        publication_link = publication.get("publication_link")

        if cover_image_link:
            if not crud_repo.delete_link(cover_image_link):
                return {"error": "Failed to delete the cover image from GitHub"}, 500

        if publication_link:
            if not crud_repo.delete_link(publication_link):
                return {"error": "Failed to delete the publication file from GitHub"}, 500

        # Delete the publication record
        if not crud_repo.delete(publication_id):
            return {"error": "Failed to delete publication"}, 500

        return {"message": "Publication deleted successfully"}, 200

   

@handle_exception
@https_fn.on_request()
def get_all_publications(request):
    
        # Fetch all publications using the CRUD repository
        publications = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not publications:
            return {"message": "No publications found"}, 404

        return {"message": "publications retrieved successfully", "publications": publications}, 200

   

@handle_exception
@https_fn.on_request()
def get_publication_by_id(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the publication publication_name from the request
        publication_id = data.get("id")
        if not publication_id:
            return {"error": "Missing required field: id"}, 400

        # Fetch the publication by publication_name using the CRUD repository
        publication = crud_repo.find_by({"id": id})
        if not publication:
            return {"error": f"publication with publication_id '{publication_id}' not found"}, 404

        return {"message": "publication retrieved successfully", "publication": publication}, 200



