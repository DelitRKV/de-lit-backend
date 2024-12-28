from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception

crud_repo = CrudRepository(collection_name="ClubTalk")

@handle_exception
@https_fn.on_request()
def create_card(request):
    
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

   
@handle_exception 
@https_fn.on_request()
def update_card(request):
    
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
        fields_to_update = {key: value for key, value in data.items() }

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
       
        id = data.get("id")

        # Update the card using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"card with name '{card_name}' not found"}, 404

        return {"message": "card updated successfully", "result": result}, 200

    

@handle_exception
@https_fn.on_request()
def delete_card(request):
    
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

        

        # Extract the ID of the card to delete
        card_id = data.get("id")

        # Delete the card using the CRUD repository
        result = crud_repo.delete(card_id)
        if not result:
            return {"error": "Failed to delete card"}, 500

        return {"message": "card deleted successfully"}, 200

    
@handle_exception
@https_fn.on_request()
def get_all_cards(request):
    
        # Fetch all cards using the CRUD repository
        cards = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not cards:
            return {"message": "No cards found"}, 404

        return {"message": "cards retrieved successfully", "cards": cards}, 200

   

@handle_exception
@https_fn.on_request()
def get_card_by_id(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the card card_name from the request
        id = data.get("id")
        if not id:
            return {"error": "Missing required field: card_name"}, 400

        # Fetch the card by card_name using the CRUD repository
        card = crud_repo.find_by({"id": id})
        if not card:
            return {"error": f"card with card_id '{id}' not found"}, 404

        return {"message": "card retrieved successfully", "card": card}, 200

   


