from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception

crud_repo = CrudRepository(collection_name="Contributions")

@handle_exception
@https_fn.on_request()
def create_contribution(request):
    
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Parse the form data
        contribution_title = request.form.get("contribution_title")
        contribution_file = request.files.get("contribution_file")
        other_data = {key: value for key, value in request.form.items() if key not in ["contribution_title", "contribution_file"]}

        # Validate inputs
        if not contribution_title:
            return {"error": "contribution title is required"}, 400

        

        # Upload the profile file (if provided)
        contribution_file_link = None
        if contribution_file:
            contribution_file_link = crud_repo.upload_file(contribution_file)
            if not contribution_file_link:
                return {"error": "Failed to upload profile file to GitHub"}, 500

        # Combine all data
        data = {"contribution_title": contribution_title, "contribution_file_link": contribution_file_link, **other_data}

        # Create the contribution in Firestore
        result = crud_repo.create(data)
        return {"message": "contribution created successfully", "result": result}, 201

   

@handle_exception
@https_fn.on_request()
def update_contribution(request):
   
        # Validate Content-Type for multipart/form-data
        if "multipart/form-data" not in request.headers.get("Content-Type", ""):
            return {"error": "Unsupported Media Type. Use 'multipart/form-data' for file uploads."}, 415

        # Extract text data and file from the request
        contribution_title = request.form.get("contribution_title")
        contribution_id = request.form.get("id")
        contribution_file = request.files.get("contribution_file")  # Extracting file file
        
        # Extract other fields dynamically
        other_fields = {key: value for key, value in request.form.items() if key not in ["contribution_title", "id", "contribution_file"]}

        # Check for required fields
        if not contribution_id:
            return {"error": "Missing required fields: contribution_title or id"}, 400

        # Fields to be updated (initially with contribution_title)
        fields_to_update = {"contribution_title": contribution_title}

        # Add other fields to update (besides contribution_title and contribution_file)
        fields_to_update.update(other_fields)

        # Handle profile file update
        if contribution_file:
            # Extract current contribution details
            contribution = crud_repo.find_by({"id": contribution_id})
            if contribution:
                old_contribution_file_link = contribution.get("contribution_file_link")

                # Delete the old profile file from GitHub if it exists
                if old_contribution_file_link:
                    cover_file_delete = crud_repo.delete_link(old_contribution_file_link)
                    if not cover_file_delete:
                        return {"error": "Failed to delete the old profile file from GitHub"}, 500

                # Upload the new profile file to GitHub
                new_file_link = crud_repo.upload_file(contribution_file)
                if not new_file_link:
                    return {"error": "Failed to upload new profile file to GitHub"}, 500
                
                # Add new profile file link to fields_to_update
                fields_to_update["contribution_file_link"] = new_file_link

        # Update the contribution details
        result = crud_repo.update(contribution_id, fields_to_update)
        if not result:
            return {"error": f"contribution with id '{contribution_id}' not found"}, 404

        return {"message": "contribution updated successfully", "result": result}, 200

   

@handle_exception
@https_fn.on_request()
def delete_contribution(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the ID of the contribution to delete
        contribution_id = data.get("id")

        # Find the contribution by ID to retrieve the profile file link
        contribution = crud_repo.find_by({"id": contribution_id})
        if not contribution:
            return {"error": "contribution not found"}, 404

        contribution_file_link = contribution.get("contribution_file_link")

        # If there is a profile file, delete it from GitHub
        if contribution_file_link:
            cover_file_delete = crud_repo.delete_link(contribution_file_link)
            if not cover_file_delete:
                return {"error": "Failed to delete the profile file from GitHub"}, 500

        # Delete the contribution using the CRUD repository
        result = crud_repo.delete(contribution_id)
        if not result:
            return {"error": "Failed to delete contribution"}, 500

        return {"message": "contribution and profile file deleted successfully"}, 200


@handle_exception
@https_fn.on_request()
def get_all_contributions(request):
    
        # Fetch all contributions using the CRUD repository
        contributions = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not contributions:
            return {"message": "No contributions found"}, 404

        return {"message": "contributions retrieved successfully", "contributions": contributions}, 200

   

@handle_exception
@https_fn.on_request()
def get_contribution_by_id(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the contribution contribution_title from the request
        contribution_id = data.get("id")
        if not contribution_id:
            return {"error": "Missing required field: contribution_id"}, 400

        # Fetch the contribution by contribution_title using the CRUD repository
        contribution = crud_repo.find_by({"id": contribution_id})
        if not contribution:
            return {"error": f"contribution with contribution_id '{contribution_id}' not found"}, 404

        return {"message": "contribution retrieved successfully", "contribution": contribution}, 200


