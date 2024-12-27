from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository

crud_repo = CrudRepository(collection_name="ClubTalk")

@https_fn.on_request()
def create_card(request):
    try:
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400
        
        card_name = data.get("card_name")
        card = crud_repo.find_by({"card_name": card_name})
        if card:
            return {"error":"card already exists"},400

       
        # Create the card using the CRUD repository
        result = crud_repo.create(data)  # Assuming crud_repo.create is synchronous
        return {"message": "card created successfully", "result": result}, 201

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
    
@https_fn.on_request()
def update_card(request):
    try:
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the card_name and check if it's provided
        card_name = data.get("card_name")
        if not card_name:
            return {"error": "Missing required field: card_name"}, 400

        # Remove card_name from the fields to update (so it's not updated itself)
        fields_to_update = {key: value for key, value in data.items() if key != "card_name"}

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
        card = crud_repo.find_by({"card_name": card_name})
        id = card.get("id")

        # Update the card using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"card with name '{card_name}' not found"}, 404

        return {"message": "card updated successfully", "result": result}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500

@https_fn.on_request()
def delete_card(request):
    try:
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the card_name and check if it's provided
        card_name = data.get("card_name")
        if not card_name:
            return {"error": "Missing required field: card_name"}, 400

        # Find the card by card_name
        card = crud_repo.find_by({"card_name": card_name})
        if not card:
            return {"error": f"card with name '{card_name}' not found"}, 404

        # Extract the ID of the card to delete
        card_id = card.get("id")

        # Delete the card using the CRUD repository
        result = crud_repo.delete(card_id)
        if not result:
            return {"error": "Failed to delete card"}, 500

        return {"message": "card deleted successfully"}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
