from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository

crud_repo = CrudRepository(collection_name="AboutUs")

@https_fn.on_request()
def create_member(request):
    try:
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400
        
        member_name = data.get("member_name")
        member = crud_repo.find_by({"member_name": member_name})
        if member:
            return {"error":"member already exists"},400

       
        # Create the member using the CRUD repository
        result = crud_repo.create(data)  # Assuming crud_repo.create is synchronous
        return {"message": "member created successfully", "result": result}, 201

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
    
@https_fn.on_request()
def update_member(request):
    try:
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the member_name and check if it's provided
        member_name = data.get("member_name")
        if not member_name:
            return {"error": "Missing required field: member_name"}, 400

        # Remove member_name from the fields to update (so it's not updated itself)
        fields_to_update = {key: value for key, value in data.items() if key != "member_name"}

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
        member = crud_repo.find_by({"member_name": member_name})
        id = member.get("id")

        # Update the member using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"member with name '{member_name}' not found"}, 404

        return {"message": "member updated successfully", "result": result}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500

@https_fn.on_request()
def delete_member(request):
    try:
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the member_name and check if it's provided
        member_name = data.get("member_name")
        if not member_name:
            return {"error": "Missing required field: member_name"}, 400

        # Find the member by member_name
        member = crud_repo.find_by({"member_name": member_name})
        if not member:
            return {"error": f"member with name '{member_name}' not found"}, 404

        # Extract the ID of the member to delete
        member_id = member.get("id")

        # Delete the member using the CRUD repository
        result = crud_repo.delete(member_id)
        if not result:
            return {"error": "Failed to delete member"}, 500

        return {"message": "member deleted successfully"}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
