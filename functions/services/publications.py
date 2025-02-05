from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception,is_url,is_github_link,cors_config

#from Utilities.email_service import send_email_to_users


crud_repo = CrudRepository(collection_name="Publications")

@handle_exception
@https_fn.on_request(cors=cors_config)
def create_publication(request):
    
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415
        
       
        
        # Extract files and form data
        image_link = request.form.get("image")
        cover_image = request.files.get("image")
        publication_file = request.files.get("file")
        publication_type = request.form.get("type")
        other_fields = {key: request.form.get(key) for key in request.form if key not in ["image","type"]}

        if  not publication_file :
            return {"error": " publication_file is  required"}, 400

        
        
        # Upload files to GitHub and get the links
       
        publication_file_link = crud_repo.upload_image(publication_file)

        if  not publication_file_link:
            return {"error": "Failed to upload files to GitHub"}, 500

        # Prepare the data for Firestore
        if cover_image or image_link:
            if(image_link != None):
                if(is_url(image_link)):
                    cover_image_link = image_link
            else:
                 cover_image_link = crud_repo.upload_image(cover_image)
            firestore_data = {
            
            "publication_type":publication_type,
            "cover_image_link": cover_image_link,
            "publication_file_link": publication_file_link,
             }
            firestore_data.update(other_fields)
            
        else:
            firestore_data = {
            
            "publication_type":publication_type,
            
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
@https_fn.on_request(cors=cors_config)
def update_publication(request):
    
         # Extract text data and file from the request
        publication_id = request.form.get("id")
        cover_image = request.files.get("image")# Extracting image file
        image_link = request.form.get("image")
        
        
        if not publication_id:
            return {"error":"publication_id not found"}, 404
        # Fetch the publication
        publication = crud_repo.find_by({"id": publication_id})
        if not publication:
            return {"error": "Publication not found"}, 404
        # Remove publication_name from the fields to update (so it's not updated itself)
        fields_to_update = {key: value for key, value in request.form.items() if key not in [ "id","image"]}

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
        
        # Handle cover image update
        if cover_image or image_link:
            # Extract current publication details
                old_cover_image_link = publication.get("cover_image_link")

                # Delete the old cover image from GitHub if it exists
                if (old_cover_image_link and is_github_link(old_cover_image_link)):
                    cover_image_delete = crud_repo.delete_link(old_cover_image_link)
                    if not cover_image_delete:
                        return {"error": "Failed to delete the old cover image from GitHub"}, 500
                    if cover_image:
                        # Upload the new cover image to GitHub
                        new_image_link = crud_repo.upload_image(cover_image)
                        if not new_image_link:
                            return {"error": "Failed to upload new profile image to GitHub"}, 500
                else:
                    new_image_link = image_link
                
                # Add new profile image link to fields_to_update
                fields_to_update["cover_image_link"] = new_image_link
       
        # Update the publication using the CRUD repository
        result = crud_repo.update(publication_id, fields_to_update)
        if not result:
            return {"error": f"Publication with id '{publication_id}' not found"}, 404

        return {"message": "Publication updated successfully", "result": result}, 200


@handle_exception
@https_fn.on_request(cors=cors_config)
def delete_publication(request):
    
        # Extract the ID of the publication to delete
        publication_id = request.args.get("id")
        if not publication_id:
            return {"error": "Publication ID is required"}, 400

        # Fetch the publication
        publication = crud_repo.find_by({"id": publication_id})
        if not publication:
            return {"error": "Publication not found"}, 404

        # Delete associated links if they exist
        cover_image_link = publication.get("cover_image_link")
        publication_link = publication.get("publication_file_link")

        if (cover_image_link and is_github_link(cover_image_link)):
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
@https_fn.on_request(cors=cors_config)
def get_all_publications(request):

        # Fetch all publications using the CRUD repository
        publication_type = request.args.get("type")
        all_publications = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection
        publications=[]
        for publication in all_publications:
            if (publication.get("publication_type")==publication_type):
                    publications.append(publication)
        if not publications:
            return {"message": "No publications found","publications":publications}, 404

        return {"message": "publications retrieved successfully", "publications": publications}, 200


@handle_exception
@https_fn.on_request(cors=cors_config)
def delete_all_publications(request):
    
    
    all_publications = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection
    
    for publication in all_publications:
        publication_id = publication.get("id")
        if not crud_repo.delete(publication_id):
            return {"message":"publication not deleted"}, 400
    return {"Message":"Successfully Delted All Publications"},200 
    
   
