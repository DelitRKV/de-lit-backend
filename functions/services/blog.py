from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository
from Utilities.utils import handle_exception,cors_config

crud_repo = CrudRepository(collection_name="Blogs")

@handle_exception
@https_fn.on_request(cors=cors_config)
def create_blog(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400
        
        title = data.get("title")
        blog = crud_repo.find_by({"title": title})
        if blog:
            return {"error":"blog already exists"},400

       
        # Create the blog using the CRUD repository
        result = crud_repo.create(data)  # Assuming crud_repo.create is synchronous
        return {"message": "blog created successfully", "result": result}, 201

    
@handle_exception
@https_fn.on_request(cors=cors_config)
def update_blog(request):
    
        # Validate Content-Type
        if request.headers.get("Content-Type") != "application/json":
            return {"error": "Unsupported Media Type"}, 415

        # Parse the request JSON
        data = request.json
        if not data:
            return {"error": "No data provided"}, 400

        # Extract the blog_name and check if it's provided
        title = data.get("title")
        if not title:
            return {"error": "Missing required field: title"}, 400

        # Remove blog_name from the fields to update (so it's not updated itself)
        fields_to_update = {key: value for key, value in data.items()}

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
       
        id = data.get("id")

        # Update the blog using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"blog with name '{title}' not found"}, 404

        return {"message": "blog updated successfully", "result": result}, 200

   

@handle_exception
@https_fn.on_request(cors=cors_config)
def delete_blog(request):
    
       

        # Extract the blog_name and check if it's provided
        id = request.args.get("id")
        if not id:
            return {"error": "Missing required field: id"}, 400

        # Find the blog by blog_name
        blog = crud_repo.find_by({"id": id})
        if not blog:
            return {"error": f"blog with if '{id}' not found"}, 404

       

        # Delete the blog using the CRUD repository
        result = crud_repo.delete(id)
        if not result:
            return {"error": "Failed to delete blog"}, 500

        return {"message": "blog deleted successfully"}, 200

    

@handle_exception
@https_fn.on_request(cors=cors_config)
def get_all_blogs(request):
   
        # Fetch all blogs using the CRUD repository
        blogs = crud_repo.get_all()  # Assuming crud_repo.find_all() returns all documents in the collection

        if not blogs:
            return {"message": "No blogs found"}, 404

        return {"message": "Blogs retrieved successfully", "blogs": blogs}, 200

@handle_exception
@https_fn.on_request(cors=cors_config)
def get_blog_by_id(request):
   
        # Validate Content-Type
        

        # Extract the blog title from the request
        id = request.args.get("id")
        if not id:
            return {"error": "Missing required field: title"}, 400

        # Fetch the blog by title using the CRUD repository
        blog = crud_repo.find_by({"id": id})
        if not blog:
            return {"error": f"Blog with id '{id}' not found"}, 404

        return {"message": "Blog retrieved successfully", "blog": blog}, 200


