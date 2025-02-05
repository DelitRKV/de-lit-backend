from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception,cors_config


crud_repo = CrudRepository(collection_name="AboutUs")

@handle_exception
@https_fn.on_request(cors=cors_config)
def create_member(request):
    
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Parse the form data
        member_name = request.form.get("member_name")
        profile_image = request.files.get("profile_image")
        other_data = {key: value for key, value in request.form.items() if key not in ["member_name", "profile_image"]}

        # Validate inputs
        if not member_name:
            return {"error": "Member name is required"}, 400

        

        # Upload the profile image (if provided)
        profile_image_link = None
        if profile_image:
            profile_image_link = crud_repo.upload_image(profile_image)
            if not profile_image_link:
                return {"error": "Failed to upload profile image to GitHub"}, 500

        # Combine all data
        data = {"member_name": member_name, "profile_image": profile_image_link, **other_data}

        # Create the member in Firestore
        result = crud_repo.create(data)
        return {"message": "Member created successfully", "result": result}, 201

   

@handle_exception
@https_fn.on_request(cors=cors_config)
def update_member(request):
    
        # Validate Content-Type for multipart/form-data
        if "multipart/form-data" not in request.headers.get("Content-Type", ""):
            return {"error": "Unsupported Media Type. Use 'multipart/form-data' for file uploads."}, 415

        # Extract text data and file from the request
        member_id = request.form.get("id")
        profile_image = request.files.get("profile_image")  # Extracting image file
        
        # Extract other fields dynamically
        other_fields = {key: value for key, value in request.form.items() if key not in [ "id", "profile_image"]}

        # Check for required fields
        if  not member_id:
            return {"error": "Missing required fields: member_name or id"}, 400

        # Fields to be updated (initially with member_name)
        fields_to_update = {}

        # Add other fields to update (besides member_name and profile_image)
        fields_to_update.update(other_fields)

        # Handle profile image update
        if profile_image:
            # Extract current member details
            member = crud_repo.find_by({"id": member_id})
            if member:
                old_profile_image_link = member.get("profile_image")

                # Delete the old profile image from GitHub if it exists
                if old_profile_image_link:
                    cover_image_delete = crud_repo.delete_link(old_profile_image_link)
                    if not cover_image_delete:
                        return {"error": "Failed to delete the old profile image from GitHub"}, 500

                # Upload the new profile image to GitHub
                new_image_link = crud_repo.upload_image(profile_image)
                if not new_image_link:
                    return {"error": "Failed to upload new profile image to GitHub"}, 500
                
                # Add new profile image link to fields_to_update
                fields_to_update["profile_image"] = new_image_link

        # Update the member details
        result = crud_repo.update(member_id, fields_to_update)
        if not result:
            return {"error": f"Member with id '{member_id}' not found"}, 404

        return {"message": "Member updated successfully", "result": result}, 200

@handle_exception
@https_fn.on_request(cors=cors_config)
def delete_member(request):
    
        # Extract the ID of the member to delete
        member_id = request.args.get("id")

        # Find the member by ID to retrieve the profile image link
        member = crud_repo.find_by({"id": member_id})
        if not member:
            return {"error": "Member not found"}, 404

        profile_image_link = member.get("profile_image")

        # If there is a profile image, delete it from GitHub
        if profile_image_link:
            cover_image_delete = crud_repo.delete_link(profile_image_link)
            if not cover_image_delete:
                return {"error": "Failed to delete the profile image from GitHub"}, 500

        # Delete the member using the CRUD repository
        result = crud_repo.delete(member_id)
        if not result:
            return {"error": "Failed to delete member"}, 500

        return {"message": "Member and profile image deleted successfully"}, 200


@handle_exception
@https_fn.on_request(cors=cors_config)
def get_all_members(request):
   
        # Fetch all members using the CRUD repository
        members = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not members:
            return {"message": "No members found"}, 404

        return {"message": "members retrieved successfully", "members": members}, 200


@handle_exception
@https_fn.on_request(cors=cors_config)
def get_member_by_id(request):
    
        # Extract the member member_name from the request
        member_id = request.args.get("id")
        if not member_id:
            return {"error": "Missing required field: member_id"}, 400

        # Fetch the member by member_name using the CRUD repository
        member = crud_repo.find_by({"id": member_id})
        if not member:
            return {"error": f"member with member_id '{member_id}' not found"}, 404

        return {"message": "member retrieved successfully", "member": member}, 200
    
@handle_exception
@https_fn.on_request(cors=cors_config)
def change_name(request):
    
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400
         # Fetch all members using the CRUD repository
        members = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection
        if not members:
            return {"message": "No members found"}, 404
        #The name of the Current Year
        batch = data.get("year")
        #The name they want to assign to the batch
        batch_name = data.get("batch_name")
        
        for member in members:
            member_id = member.get("id")
            if(member.get("year")==batch):
                update={"batch":batch_name}
                if not crud_repo.update(member_id,update):
                    return {"message": f"Failed to update the member with member_id '{member_id}'"},404
        return {"message":"Successfully changed the batch_name"},200
                            
                
            
        
        


