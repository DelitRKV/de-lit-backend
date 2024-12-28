from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception

crud_repo = CrudRepository(collection_name="Banner")

@handle_exception
@https_fn.on_request()
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
        
        if banner_file:
            
            # Check if banner already exists using the provided ID
            existing_banner = crud_repo.find_by({"id": banner_id}) if banner_id else None

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
            banner_data = {
                "banner_link": banner_image_link,
                "quote": banner_quote,
            }
        else:
            banner_data = {
                "quote":banner_quote
            }

        if banner_id:
            # Update the existing banner
            result = crud_repo.update(banner_id, banner_data)
            message = "Banner updated successfully"
        else:
            # Create a new banner
            result = crud_repo.create(banner_data)
            message = "Banner created successfully"

        return {
            "message": message,
            "firestore_result": result,
        }, 201

  
