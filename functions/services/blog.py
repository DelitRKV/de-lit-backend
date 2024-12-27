from firebase_functions import https_fn
from Utilities.crud_repo import CrudRepository

crud_repo = CrudRepository(collection_name="Blogs")

@https_fn.on_request()
def create_blog(request):
    try:
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

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
    
@https_fn.on_request()
def update_blog(request):
    try:
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
        fields_to_update = {key: value for key, value in data.items() if key != "title"}

        if not fields_to_update:
            return {"error": "No fields to update provided"}, 400
        blog = crud_repo.find_by({"title": title})
        id = blog.get("id")

        # Update the blog using the CRUD repository
        result = crud_repo.update(id, fields_to_update)
        if not result:
            return {"error": f"blog with name '{title}' not found"}, 404

        return {"message": "blog updated successfully", "result": result}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500

@https_fn.on_request()
def delete_blog(request):
    try:
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

        # Find the blog by blog_name
        blog = crud_repo.find_by({"title": title})
        if not blog:
            return {"error": f"blog with name '{title}' not found"}, 404

        # Extract the ID of the blog to delete
        blog_id = blog.get("id")

        # Delete the blog using the CRUD repository
        result = crud_repo.delete(blog_id)
        if not result:
            return {"error": "Failed to delete blog"}, 500

        return {"message": "blog deleted successfully"}, 200

    except Exception as e:
        return {"error": f"Internal Server Error: {str(e)}"}, 500
