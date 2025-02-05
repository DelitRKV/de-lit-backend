from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception,cors_config

crud_repo = CrudRepository(collection_name="ClubTalk")


@handle_exception
@https_fn.on_request(cors=cors_config)
def create_card(request):
    
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Parse the form data
        title = request.form.get("title")
        profile_image = request.files.get("profile_image")
        other_data = {key: value for key, value in request.form.items() if key not in ["title", "profile_image"]}

        # Validate inputs
        if not title:
            return {"error": "title is required"}, 400

        

        # Upload the profile image (if provided)
        profile_image_link = None
        if profile_image:
            profile_image_link = crud_repo.upload_image(profile_image)
            if not profile_image_link:
                return {"error": "Failed to upload profile image to GitHub"}, 500

        # Combine all data
        data = {"title": title, "profile_image": profile_image_link, **other_data}

        # Create the member in Firestore
        result = crud_repo.create(data)
        return {"message": "Member created successfully", "result": result}, 201


   
@handle_exception
@https_fn.on_request(cors=cors_config)
def update_card(request):
    
        # Validate Content-Type for multipart/form-data
        if "multipart/form-data" not in request.headers.get("Content-Type", ""):
            return {"error": "Unsupported Media Type. Use 'multipart/form-data' for file uploads."}, 415

        # Extract text data and file from the request
        
        card_id = request.form.get("id")
        profile_image = request.files.get("profile_image")  # Extracting image file
        
        # Extract other fields dynamically
        other_fields = {key: value for key, value in request.form.items() if key not in [ "id", "profile_image"]}

        # Check for required fields
        if  not card_id:
            return {"error": "Missing required fields:  id"}, 400

        # Fields to be updated 
        fields_to_update = {}

        # Add other fields to update (besides title and profile_image)
        fields_to_update.update(other_fields)

        # Handle profile image update
        if profile_image:
            # Extract current member details
            member = crud_repo.find_by({"id": card_id})
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
        result = crud_repo.update(card_id, fields_to_update)
        if not result:
            return {"error": f" card with id '{card_id}' not found"}, 404

        return {"message": "Card updated successfully", "result": result}, 200
    

@handle_exception
@https_fn.on_request(cors=cors_config)
def delete_card(request):
    
        # Extract the ID of the card to delete
        card_id = request.args.get("id")

        # Find the card by ID to retrieve the profile image link
        member = crud_repo.find_by({"id": card_id})
        if not member:
            return {"error": "Card not found"}, 404

        profile_image_link = member.get("profile_image")

        # If there is a profile image, delete it from GitHub
        if profile_image_link:
            cover_image_delete = crud_repo.delete_link(profile_image_link)
            if not cover_image_delete:
                return {"error": "Failed to delete the profile image from GitHub"}, 500

        # Delete the member using the CRUD repository
        result = crud_repo.delete(card_id)
        if not result:
            return {"error": "Failed to delete card"}, 500

        return {"message": "Card and profile image deleted successfully"}, 200


    
@handle_exception
@https_fn.on_request(cors=cors_config)
def get_all_cards(request):
    
        # Fetch all cards using the CRUD repository
        cards = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not cards:
            return {"message": "No cards found"}, 404

        return {"message": "cards retrieved successfully", "cards": cards}, 200

   

@handle_exception
@https_fn.on_request(cors=cors_config)
def get_card_by_id(request):
    
        # Extract the card card_name from the request
        id = request.args.get("id")
        if not id:
            return {"error": "Missing required field: card_name"}, 400

        # Fetch the card by card_name using the CRUD repository
        card = crud_repo.find_by({"id": id})
        if not card:
            return {"error": f"card with card_id '{id}' not found"}, 404

        return {"message": "card retrieved successfully", "card": card}, 200

   


