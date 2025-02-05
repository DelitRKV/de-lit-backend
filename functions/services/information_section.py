from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception,cors_config

crud_repo = CrudRepository(collection_name="Information_Section")

@handle_exception
@https_fn.on_request(cors=cors_config)
def create_info(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400
        
        # Create the info using the CRUD repository
        result = crud_repo.create(data)  # Assuming crud_repo.create is synchronous
        return {"message": "info created successfully", "result": result}, 201

    
@handle_exception
@https_fn.on_request(cors=cors_config)
def update_info(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the info_name and check if it's provided
        id = data.get("id")
        if not id:
            return {"error": "Missing required field: id"}, 400

        # Remove info_name from the fields to update (so it's not updated itself)
        fields_to_update = {key: value for key, value in data.items()}

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
       
        

        # Update the info using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"info with id '{id}' not found"}, 404

        return {"message": "info updated successfully", "result": result}, 200

   

@handle_exception
@https_fn.on_request(cors=cors_config)
def delete_info(request):
    
       

        # Extract the info_name and check if it's provided
        id = request.args.get("id")
        if not id:
            return {"error": "Missing required field: id"}, 400

        # Find the info by info_name
        info = crud_repo.find_by({"id": id})
        if not info:
            return {"error": f"info with if '{id}' not found"}, 404

       

        # Delete the info using the CRUD repository
        result = crud_repo.delete(id)
        if not result:
            return {"error": "Failed to delete info"}, 500

        return {"message": "info deleted successfully"}, 200

    

@handle_exception
@https_fn.on_request(cors=cors_config)
def get_all_infos(request):
   
        # Fetch all infos using the CRUD repository
        infos = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not infos:
            return {"message": "No infos found"}, 404

        return {"message": "infos retrieved successfully", "infos": infos}, 200

@handle_exception
@https_fn.on_request(cors=cors_config)
def get_info_by_id(request):
   
        # Validate Content-Type
        

        # Extract the info title from the request
        id = request.args.get("id")
        if not id:
            return {"error": "Missing required field: title"}, 400

        # Fetch the info by title using the CRUD repository
        info = crud_repo.find_by({"id": id})
        if not info:
            return {"error": f"info with id '{id}' not found"}, 404

        return {"message": "info retrieved successfully", "info": info}, 200


