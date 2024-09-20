from flask import Flask, jsonify , request ,send_from_directory , abort
from flask_restful import Api, Resource
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token
from bson import ObjectId
import re
import os
current_directory = os.getcwd()
front_end_folder = os.path.abspath(os.path.join(current_directory, "frontend", "build"))

app = Flask(__name__, static_folder=os.path.join(front_end_folder, 'static'))
CORS(app, supports_credentials=True, origins='*')

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', '#9G8G8LLVJ@pg')  # Default value for development
jwt = JWTManager(app)

app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb+srv://parthgupta221092:9G8G8LLVJ@ecommerce-cluster.wjmddqr.mongodb.net/Social-Geathering-App?retryWrites=true&w=majority')
mongo = PyMongo(app)

users = mongo.db.users
personalInfo = mongo.db.personalInfo
contactInfo = mongo.db.contactInfo
# fs = GridFS(mongo.db)
api = Api(app)


def check_file_permissions(file_path):
    if os.access(file_path, os.R_OK):
        print(f"File '{file_path}' is readable by the Flask server process.")
    else:
        print(f"Warning: File '{file_path}' is not readable by the Flask server process. Please check permissions.")

# Get frontend folder path

# Print the contents of the front_end_folder for debugging
try:
    contents = os.listdir(front_end_folder)
    print("Contents of the frontend build directory:", contents)
except FileNotFoundError as e:
    print("Error:", e)
    print("The directory does not exist.")

@app.route('/', defaults={"filename": ""})
@app.route('/<path:filename>')
def index(filename):
    print(filename)
    if not filename or not os.path.exists(os.path.join(front_end_folder, filename)):
        filename = "index.html"
    file_path = os.path.join(front_end_folder, filename)
    print("Requested file path:", file_path)  # Debugging requested file path
    if not os.path.exists(file_path):
        print("File not found:", file_path)  # Debugging file existence
        return abort(404)  # Return 404 if file is not found
    return send_from_directory(front_end_folder, filename)


@app.route('/static/<path:filename>')
def serve_static(filename):
    print("Requested static file:", filename)
    try:
        static_folder = os.path.join(front_end_folder, 'static')
        file_path = os.path.join(static_folder, filename)
        print("Static folder path:", static_folder)  # Debugging static folder path
        print("Requested static file path:", file_path)  # Debugging requested file path

        if not os.path.exists(file_path):
            print("Static file not found:", file_path)  # Debugging file existence
            return abort(404)  # Return 404 if file is not found

        check_file_permissions(file_path)  # Check file permissions
        return send_from_directory(static_folder, filename)
    except Exception as e:
        print("Error serving static file:", e)  # Debugging any other errors
        return abort(500)  # Return 500 for any other server errors


class Users(Resource):
    def post(self):
        data =  request.get_json()
        # if "आधार नंबर" not in data:
        #     return jsonify({'error': 'No image uploaded Or No Aadhar Number'}), 400
        # if users.find_one({"आधार नंबर": data["आधार नंबर"]}):
        #     return {"message": "Username already exists"}, 409

        # Insert the new user into the database
        users.insert_one(data)
        return {"message": "User created successfully"}, 201

        return jsonify({'message': 'Image uploaded and compressed successfully', 'inserted_id': str(inserted_id)}), 200

    def get(self):
        query = request.args.get("search")
        regex = re.compile(query, re.IGNORECASE)  # create a regex object, case-insensitive
        results = users.find({"मो": regex})

        result_list = []
        for result in results:
            result["_id"] = str(result["_id"])
            # print(result)
            result_list.append(result)

        return {
            "query": result_list
        }


class Profile(Resource):
    def get(self):
        id = request.args.get("id")
        user = users.find_one({"_id": ObjectId(id)})

        if user:
            user["_id"] = str(user["_id"])
            return {"user": user}, 200
        else:
            return {"message": "No user found"}, 404
class Edit(Resource):
    def post(self):
        uid = request.args.get("id")
        data = request.get_json()
        print(uid,data)
        if not uid or not data:
            return {"message": "ID or data not found"}, 404
        try:
            # Convert the ID to an ObjectId
            user_id = ObjectId(uid)
        except:
            return {"message": "Invalid ID format"}, 400
        result = users.update_one({"_id": user_id}, {"$set": data})

        if result.matched_count == 0:
            return {"message": "User not found"}, 404

        return {"message": "User updated successfully"}, 200


api.add_resource(Users , "/user")
# api.add_resource(Image)
api.add_resource(Profile, "/profile")
api.add_resource(Edit, "/updateuser")

if __name__ == '__main__':
    app.run(debug=True, port=8080)

