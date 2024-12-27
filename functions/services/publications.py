from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository

crud_repo = CrudRepository(collection_name="Publications")

@https_fn.on_request()
def create_publication(request):
    try:
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400
        
        publication_name = data.get("publication_name")
        publication = crud_repo.find_by({"publication_name": publication_name})
        if publication:
            return {"error":"publication already exists"},400

       
        # Create the publication using the CRUD repository
        result = crud_repo.create(data)  # Assuming crud_repo.create is synchronous
        return {"message": "Publication created successfully", "result": result}, 201

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
    
@https_fn.on_request()
def update_publication(request):
    try:
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
        fields_to_update = {key: value for key, value in data.items() if key != "publication_name"}

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
        publication = crud_repo.find_by({"publication_name": publication_name})
        id = publication.get("id")

        # Update the publication using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"Publication with name '{publication_name}' not found"}, 404

        return {"message": "Publication updated successfully", "result": result}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500

@https_fn.on_request()
def delete_publication(request):
    try:
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

        # Find the publication by publication_name
        publication = crud_repo.find_by({"publication_name": publication_name})
        if not publication:
            return {"error": f"Publication with name '{publication_name}' not found"}, 404

        # Extract the ID of the publication to delete
        publication_id = publication.get("id")

        # Delete the publication using the CRUD repository
        result = crud_repo.delete(publication_id)
        if not result:
            return {"error": "Failed to delete publication"}, 500

        return {"message": "Publication deleted successfully"}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
