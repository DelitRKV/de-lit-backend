from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception

crud_repo = CrudRepository(collection_name="Feedbacks")

@handle_exception
@https_fn.on_request()
def create_feedback(request):
  
        # Validate Content-Type
        content_type = request.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {"error": "Unsupported Media Type"}, 415

        # Parse the form data
        feedback_title = request.form.get("feedback_title")
        feedback_file = request.files.get("feedback_file")
        other_data = {key: value for key, value in request.form.items() if key not in ["feedback_title", "feedback_file"]}

        # Validate inputs
        if not feedback_title:
            return {"error": "feedback title is required"}, 400

        

        # Upload the profile file (if provided)
        feedback_file_link = None
        if feedback_file:
            feedback_file_link = crud_repo.upload_file(feedback_file)
            if not feedback_file_link:
                return {"error": "Failed to upload profile file to GitHub"}, 500

        # Combine all data
        data = {"feedback_title": feedback_title, "feedback_file_link": feedback_file_link, **other_data}

        # Create the feedback in Firestore
        result = crud_repo.create(data)
        return {"message": "feedback created successfully", "result": result}, 201

@handle_exception
@https_fn.on_request()
def update_feedback(request):
    
        # Validate Content-Type for multipart/form-data
        if "multipart/form-data" not in request.headers.get("Content-Type", ""):
            return {"error": "Unsupported Media Type. Use 'multipart/form-data' for file uploads."}, 415

        # Extract text data and file from the request
        feedback_title = request.form.get("feedback_title")
        feedback_id = request.form.get("id")
        feedback_file = request.files.get("feedback_file")  # Extracting file file
        
        # Extract other fields dynamically
        other_fields = {key: value for key, value in request.form.items() if key not in ["feedback_title", "id", "feedback_file"]}

        # Check for required fields
        if not feedback_id:
            return {"error": "Missing required fields: feedback_title or id"}, 400

        # Fields to be updated (initially with feedback_title)
        fields_to_update = {"feedback_title": feedback_title}

        # Add other fields to update (besides feedback_title and feedback_file)
        fields_to_update.update(other_fields)

        # Handle profile file update
        if feedback_file:
            # Extract current feedback details
            feedback = crud_repo.find_by({"id": feedback_id})
            if feedback:
                old_feedback_file_link = feedback.get("feedback_file_link")

                # Delete the old profile file from GitHub if it exists
                if old_feedback_file_link:
                    cover_file_delete = crud_repo.delete_link(old_feedback_file_link)
                    if not cover_file_delete:
                        return {"error": "Failed to delete the old profile file from GitHub"}, 500

                # Upload the new profile file to GitHub
                new_file_link = crud_repo.upload_file(feedback_file)
                if not new_file_link:
                    return {"error": "Failed to upload new profile file to GitHub"}, 500
                
                # Add new profile file link to fields_to_update
                fields_to_update["feedback_file_link"] = new_file_link

        # Update the feedback details
        result = crud_repo.update(feedback_id, fields_to_update)
        if not result:
            return {"error": f"feedback with id '{feedback_id}' not found"}, 404

        return {"message": "feedback updated successfully", "result": result}, 200

    

@https_fn.on_request()
def delete_feedback(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the ID of the feedback to delete
        feedback_id = data.get("id")

        # Find the feedback by ID to retrieve the profile file link
        feedback = crud_repo.find_by({"id": feedback_id})
        if not feedback:
            return {"error": "feedback not found"}, 404

        feedback_file_link = feedback.get("feedback_file_link")

        # If there is a profile file, delete it from GitHub
        if feedback_file_link:
            cover_file_delete = crud_repo.delete_link(feedback_file_link)
            if not cover_file_delete:
                return {"error": "Failed to delete the profile file from GitHub"}, 500

        # Delete the feedback using the CRUD repository
        result = crud_repo.delete(feedback_id)
        if not result:
            return {"error": "Failed to delete feedback"}, 500

        return {"message": "feedback and profile file deleted successfully"}, 200

    

@handle_exception
@https_fn.on_request()
def get_all_feedbacks(request):
    
        # Fetch all feedbacks using the CRUD repository
        feedbacks = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not feedbacks:
            return {"message": "No feedbacks found"}, 404

        return {"message": "feedbacks retrieved successfully", "feedbacks": feedbacks}, 200


@handle_exception
@https_fn.on_request()
def get_feedback_by_id(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the feedback feedback_title from the request
        feedback_id = data.get("id")
        if not feedback_id:
            return {"error": "Missing required field: feedback_id"}, 400

        # Fetch the feedback by feedback_title using the CRUD repository
        feedback = crud_repo.find_by({"id": feedback_id})
        if not feedback:
            return {"error": f"feedback with feedback_id '{feedback_id}' not found"}, 404

        return {"message": "feedback retrieved successfully", "feedback": feedback}, 200

    

