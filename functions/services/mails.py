from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception


crud_repo = CrudRepository(collection_name="E-Mails")

@handle_exception
@https_fn.on_request()
def upload_mail(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400
        
        email = data.get("email")
        user = crud_repo.find_by({"email": email})
        if user:
            return {"error":"email_id already exists"},400

       
       
        result = crud_repo.create(data)# Assuming crud_repo.create is synchronous
        
        return {"message": "Email_ID Uploaded successfully", "result": result}, 201
    

@handle_exception
@https_fn.on_request()
def get_all_emails(request):
   
        # Fetch all mails using the CRUD repository
        emails = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not emails:
            return {"message": "No emails found"}, 404

        return {"message": "Emails retrieved successfully", "emails": emails}, 200
    
    
def get_all_emailss():
   
        # Fetch all mails using the CRUD repository
        emails = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not emails:
            return {"message": "No emails found"}, 404

        return {"message": "Emails retrieved successfully", "emails": emails}, 200