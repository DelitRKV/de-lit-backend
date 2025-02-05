from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception,cors_config
#from Utilities.email_service import send_email_to_users

crud_repo = CrudRepository(collection_name="Banner")

@handle_exception
@https_fn.on_request(cors=cors_config)
def upload_banner(request):
    # Validate Content-Type
    content_type = request.headers.get("Content-Type", "")
    if "multipart/form-data" not in content_type:
        return {"error": "Unsupported Media Type"}, 415

    # Extract file and description
    banner_file = request.files.get("banner")
    banner_quote = request.form.get("quote")
    banner_id = request.form.get("id")  # Banner ID to check existence
    print("Files received:", request.files)
    print("Form data received:", request.form)
    
    # Check if a banner file is provided
    #if not banner_file:
        #return {"error": "Banner file is required"}, 400
    banner_data={}
    if banner_file:
        # Check if banner already exists using the provided ID
        existing_banner = crud_repo.find_by({"id": banner_id})
        if existing_banner:
            # If it exists, delete the old banner image from GitHub
            old_banner_link = existing_banner.get("banner_link")
            if old_banner_link:
                delete_result = crud_repo.delete_link(old_banner_link)
                if not delete_result:
                    return {"error": "Failed to delete the old banner image from GitHub"}, 500

    # Upload new banner image to GitHub
        banner_image_link = crud_repo.upload_image(banner_file)
        if not banner_image_link:
            return {"error": "Failed to upload banner image to GitHub"}, 500

        # Prepare data for Firestore
        banner_data = {"banner_link": banner_image_link}
    
        
   
    if banner_quote:
        banner_data["quote"] = banner_quote  # Only include quote if provided

    if banner_id:
        # Update the existing banner
        result = crud_repo.update(banner_id, banner_data)
        if result:
            return {"message": "Banner updated successfully", "firestore_result": result}, 200
        else:
            return {"error": "Failed to update banner in Firestore"}, 500
    else:
        # Create a new banner
        result = crud_repo.create(banner_data)
        if result:
            return {"message": "Banner created successfully", "firestore_result": result}, 201
        else:
            return {"error": "Failed to create banner in Firestore"}, 500

  
@handle_exception
@https_fn.on_request(cors=cors_config)
def get_banner(request):
   
        # Fetch  banner using the CRUD repository
        banner = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not banner:
            return {"message": "No banner found"}, 404

        return {"message": "banner retrieved successfully", "banner": banner}, 200