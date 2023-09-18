# Student Start ========================

from flask import Flask, jsonify, request, render_template,session
from pymongo import  errors
import os
import hashlib
from bson import ObjectId
from flask_pymongo import PyMongo
from teacherdb import create_user,update_user,get_user
from teacherdb import create_user,update_user,get_user

from parentdb import create_parent, update_parent,get_parents,get_parent_by_password_and_useridname,get_parent
# ,get_student_data_by_parent_useridname

from werkzeug.utils import secure_filename
from werkzeug .security import generate_password_hash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = "Technologies"
app.config["MONGO_URI"] = "mongodb+srv://sourav:sourav@cluster0.6aannpk.mongodb.net/Students"
mongo_S = PyMongo(app)

app.config['MONGO_URI'] = 'mongodb+srv://sourav:sourav@cluster0.6aannpk.mongodb.net/Quizz'
mongo_q = PyMongo(app)

UPLOAD_FOLDER = 'static'  # Folder to store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'jfif'}  # Allowed file extensions for images
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Create unique indexes for user_id, personal_info.contact.phone, and personal_info.contact.email
mongo_S.db.student_profile.create_index([("user_id", 1)], unique=True)
mongo_S.db.student_profile.create_index([("personal_info.contact.phone", 1)], unique=True, partialFilterExpression={"personal_info.contact.phone": {"$exists": True}})
mongo_S.db.student_profile.create_index([("personal_info.contact.email", 1)], unique=True, partialFilterExpression={"personal_info.contact.email": {"$exists": True}})


# functions to support API's
def is_user_id_unique(user_id):
    # Query your database to check if the user_id already exists
    user = get_student(user_id)
    return user

def get_student(user_id):
    user = mongo_S.db.student_profile.find_one({'user_id': user_id})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to a string
    return jsonify(user)

def search_by_mobile_number(number):
    query = {
        "personal_info.contact.phone": number
    }
    # Use the find() method to retrieve matching documents
    matching_documents = mongo_S.db.student_profile.find(query)
    result = [document for document in matching_documents]
    return result


def search_by_email(email):
    query = {
        "personal_info.contact.email": email
    }
    # Use the find() method to retrieve matching documents
    matching_documents = mongo_S.db.student_profile.find(query)
    result = [document for document in matching_documents]
    return result

def search_by_username_or_user_id(user):
    result = []
    # First, search for user IDs
    user_id_query = {
        "user_id": user
    }
    user_id_matching_documents = mongo_S.db.student_profile.find(user_id_query)
    result.extend(user_id_matching_documents)
    # Then, search for usernames
    username_query = {
        "username": user
    }
    username_matching_documents = mongo_S.db.student_profile.find(username_query)
    result.extend(username_matching_documents)
    # Return the combined result list
    return result

def get_students():
    return list(mongo_S.db.student_profile.find())

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image(image):
    if image and allowed_file(image.filename):
        filename = f"{ObjectId()}.{image.filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "Image uploaded successfully.", "filename": filename}), 200
    else:
        return jsonify({"message": "Invalid image or file format."}), 400


def hash_password(password):
    # Create a new SHA-256 hash object
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    hashed_password = sha256.hexdigest()
    return hashed_password  

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

# Create student profile 
@app.route('/student/create_student_profile', methods=['POST'])
def create_student_profile():
    user_id = request.form.get('user_id', '')
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    hashed_password = hash_password(password)
    user_class = request.form.get('user_class', '')
    # unknown_field = request.form.get('do not know yet')
    status_title = request.form.get('status_title', '')
    status_description = request.form.get('status_description', '')
    about = request.form.get('about', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    parents = request.form.get('parents', '')

    if not is_user_id_unique(user_id):
        return jsonify({'error': 'User ID already exists'}), 400
    
    user_image = ''
    if request.form.get('image',''):
        image = request.form.get('image','')
        user_image = upload_image(image)

    performance = {} 
    Attendance = {}
    Interest = {}
    parents = {}

    user_data = {
        "_id": str(ObjectId()),
        'user_id':user_id,
        'password': hashed_password,
        'username': username,
        'user_class': user_class,
        'user_image': user_image,
        'status_title': status_title,
        'status_description': status_description,
        'personal_info': {
            'about': about,
            'contact': {
                'phone': phone,
                'email': email,
                'address': address
            }
        },
        'performance': performance,
        'Attendance': Attendance,
        'Interest': Interest,
        'parents': parents
    }
    try:
        inserted_id = mongo_S.db.student_profile.insert_one(user_data).inserted_id
        inserted = mongo_S.db.student_profile.find_one({"_id": inserted_id})
        return jsonify({"_id": str(inserted["_id"])})
    except Exception as e:
        print(e)
        return jsonify({"error": "Error occurred while creating the class"}), 500

# Get student profile using user_id
@app.route('/student/get_user/<string:user_id>', methods=['GET'])
def get_user_profile(user_id):
    return get_student(user_id)

# update user profiledata requires user_id which is Unique
@app.route('/student/update_student_profile/<string:user_id>', methods=['PUT'])
def update_student_profile(user_id):
    try:
        user_data = mongo_S.db.student_profile.find_one({'user_id': user_id})
        _id = user_data['_id']
        # Get user data from the request
        username = request.form.get('username', user_data['username'])
        password = request.form.get('password', user_data['password'])
        hashed_password = hash_password(password)
        user_id = request.form.get('user_id', user_data['user_id'])

        user_class = request.form.get('user_class', user_data['user_class'])
        status_title = request.form.get('status_title', user_data['status_title'])
        status_description = request.form.get('status_description', user_data['status_description'])
        about = request.form.get('about', user_data['personal_info']['about'])
        phone = request.form.get('phone', user_data['personal_info']['contact']['phone'])
        email = request.form.get('email', user_data['personal_info']['contact']['email'])
        address = request.form.get('address', user_data['personal_info']['contact']['address'])
        performance = request.form.get('performance', user_data['performance'])
        Interest = request.form.get('Interest', user_data['Interest'])
        Attendance = request.form.get('Attendance', user_data['Attendance'])
        parents = request.form.get('parents', user_data['parents'])

        # Optional: Handle the user image update
        user_image = ''
        if request.form.get('image', user_data['user_image']):
            image = request.form.get('image','')
            user_image = upload_image(image)

        user_data ={
                'user_id':user_id,
                'username': username,
                'password':hashed_password,
                'user_class': user_class,
                'user_image': user_image,
                'status_title': status_title,
                'status_description': status_description,
                'personal_info': {
                    'about': about,
                    'contact': {
                        'phone': phone,
                        'email': email,
                        'address': address
                    }
                },
                'performance': performance,
                'Attendance': Attendance,
                'Interest': Interest,
                'parents': parents
            }
        result = mongo_S.db.student_profile.update_one({"_id":_id},
                                                    {"$set": user_data})
        if result.modified_count == 0:
            return jsonify({"error": "student_profile not found"}), 404
        updated_entity = mongo_S.db.student_profile.find_one({"_id": _id})
        return jsonify(updated_entity), 200
    except errors.PyMongoError as e:
        return jsonify({"error": str(e)}), 500


# search other user using phone, email, userid, username
@app.route('/student/search/<string:query>', methods=['GET'])
def search(query):
    # query = request.args.get('query', '').strip()
    try:
        if query:
            # Check if the query is a valid mobile number (all digits)
            if query.isdigit() and len(query) == 10:
                # Search for mobile number in all collections (student, parents, teacher)
                result = search_by_mobile_number(query)
            elif '@' in query:
                # Check if the query contains "@" (likely an email)
                # Search for email in all collections
                result = search_by_email(query)
            else:
                # Search for username or user ID in all collections
                result = search_by_username_or_user_id(query)
            return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500


# setting status of quiz after click by user on quiz 
@app.route('/student/setting_status/<string:quiz_id>/<string:student_id>', methods = ['PUT'])
def setting_status_of_quizz(quiz_id, student_id):

    new_quiz = {
        "quiz_id": quiz_id,
        "status": "seen"
    }

    # Define the update operation to add the new quiz to the quiz_data array
    update = {
        '$push': {
            'quiz_data': {
                '$each': [new_quiz],
            }
        }
    }

    result = mongo_S.db.student_profile.update_one({'_id': student_id}, update)
    return "Quizz seen",200


#adding quizz in student profile
@app.route('/student/update_student_quiz_data/<string:quiz_id>/<string:student_id>/<string:result>/<string:click>', methods=['PUT'])
def update_student_quiz_data(quiz_id, student_id, result, click):
    try:
        # Find the student by student_id
        student = mongo_S.db.student_profile.find_one({"_id": student_id})
        
        if student:
            # Check if the quiz_id already exists in quiz_data
            quiz_entry = next((entry for entry in student['quiz_data'] if entry.get('quiz_id') == quiz_id), None)

            if quiz_entry:
                quiz = mongo_q.db.quizes.find_one({"_id": quiz_id})
                # Update the existing quiz entry
                quiz_entry['subject'] = quiz.get('subject', '')
                quiz_entry['topic'] = quiz.get('topic', '')
                quiz_entry['class'] = quiz.get('class', '')
                quiz_entry['subtopic'] = quiz.get('subtopic', '')
                quiz_entry['language'] = quiz.get('language', '')            
                quiz_entry['result'] = result
                quiz_entry['clicked_on'] = click
                print(student)

                # Update the student's document with the modified quiz_data
                mongo_S.db.student_profile.update_one({"_id": student_id}, {"$set": student})

                return jsonify({"message": "Student quiz data updated successfully."}), 200
            else:
                return jsonify({"message": "Quiz not found in student data."}), 404
        else:
            return jsonify({"message": "Student not found."}), 404

    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500


# getting accuracy of student
@app.route('/student/getting_accuracy/<string:student_id>', methods=['GET'])
def getting_accuracy(student_id):
    try:
        student = mongo_S.db.student_profile.find_one({"_id": student_id})
        result = []
        for res in student.get("quiz_data", []):
            try:
                result.append(res['result'])
            except KeyError:
                # Key 'result' not found in this quiz data, continue to the next iteration
                continue
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"message": "An error occurred.", "error": str(e)}), 500



# ==============STUBENT END=================


# TeachEr Start=================================================


@app.route('/teacher')
def hometeacher():
    return render_template('teacher/index.html')



@app.route('/teacher/create_user', methods=['GET', 'POST'])
def create_profile():
    username = request.form.get('username', '')
    # user_class = request.form.get('user_class', '')
    language = request.form.get('language','')
    call_icon = request.form.get('call_icon','')
    message_icon = request.form.get('message_icon','')
    
    user_designation = request.form.get('user_designation', '')
    user_description = request.form.get('user_description', '')
    about = request.form.get('user_about', '')
    useridname = request.form.get('useridname', '')
    password = request.form.get('password', '')
    
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')
    department = request.form.get('department', '')
    experience = request.form.get('experience', '')
    specialization = request.form.get('specialization', '')
    totalClasses = request.form.get('totalClasses', '')
    attendedClasses = request.form.get('attendedClasses', '')
    Topic1 = request.form.get('topic1', '')
    Topic2 = request.form.get('topic2', '')
    award = request.form.get('award', '')
    hobbies = request.form.get('hobbies', '')
    favoriteTopic = request.form.get('favoriteTopic', '')


    user_image = request.files['file']
    if user_image:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(user_image.filename))
        user_image.save(filename)

    personal_info = {
        'status':{
            'user_designation':user_designation,
            'user_description':user_description
        },
        'about': about,
        'useridpassword':{
            'useridname':useridname,
            'password':password
        },
        'contact': {
            'phone': phone,
            'email': email,
            'address': address
        }
    }
    academic = {
        'department': department,
        'experience': experience,
        'specialization': specialization
    },
    attendence= {
        'totalClasses': totalClasses,
        'attendedClasses': attendedClasses,
    }
    performance={
            'classGrades': {
                'topic1': Topic1,
                'topic2': Topic2
            },
            'award':award
    }
    interest={
        'hobbies': hobbies,
        'favoriteTopic': favoriteTopic,
    }
    user_data = {
        'username': username,
        'language':language,
        'call_icon':call_icon,
        'message_icon':message_icon,
        # 'user_class': user_class,
        'user_image': filename,
        'user_designation': user_designation,
        'user_description': user_description,
        'personal_info': personal_info,
        'academic':academic,
        'attendence': attendence,
        'performance':performance,
        'interest':interest
    }

    create_user(username,language, call_icon, message_icon, filename, user_designation, user_description, about,useridname, password, phone, email, address, department,
                    experience, specialization,totalClasses,attendedClasses,Topic1,Topic2,award,hobbies,favoriteTopic)

    # return jsonify({'user_data': user_data})
    return jsonify(user_data)

@app.route('/teacher/get_user/<string:user_id>', methods=['GET'])
def get_teacher_profile(user_id):
    # Call the get_user function to retrieve the user's profile by user ID
    user = get_user(user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify(user)

@app.route('/teacher/update_user/<string:user_id>', methods=['PUT', 'POST'])
def update_user_profile(user_id):
    user_data = get_user(user_id)

    if not user_data:
        return jsonify({"error": "User not found"}), 404

    username = request.form.get('username', user_data['username'])
    language = request.form.get('language', user_data['language'])
    call_icon = request.form.get('call_icon', user_data['call_icon'])
    message_icon = request.form.get('message_icon', user_data['message_icon'])

    user_designation = request.form.get('user_designation', user_data['personal_info']['status']['user_designation'])
    user_description = request.form.get('user_description', user_data['personal_info']['status']['user_description'])
    about = request.form.get('user_about', user_data['personal_info']['about'])
    useridname = request.form.get('useridname', user_data['personal_info']['useridpassword']['useridname'])
    password = request.form.get('password', user_data['personal_info']['useridpassword']['password'])
    phone = request.form.get('phone', user_data['personal_info']['contact']['phone'])
    email = request.form.get('email', user_data['personal_info']['contact']['email'])
    address = request.form.get('address', user_data['personal_info']['contact']['address'])
    department = request.form.get('department', user_data['academic']['department'])
    experience = request.form.get('experience', user_data['academic']['experience'])
    specialization = request.form.get('specialization', user_data['academic']['specialization'])
    totalClasses = request.form.get('totalClasses', user_data['attendence']['totalClasses'])
    attendedClasses = request.form.get('attendedClasses', user_data['attendence']['attendedClasses'])
    Topic1 = request.form.get('topic1', user_data['performance']['classGrades']['topic1'])
    Topic2 = request.form.get('topic2', user_data['performance']['classGrades']['topic2'])
    award = request.form.get('award', user_data['performance']['award'])
    hobbies = request.form.get('hobbies', user_data['interest']['hobbies'])
    favoriteTopic = request.form.get('favoriteTopic', user_data['interest']['favoriteTopic'])

    user_image = request.files.get('file')
    filename = user_data.get('user_image')  # Get the existing filename

    if user_image:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(user_image.filename))
        user_image.save(filename)

    update_user(user_id, username, language, call_icon, message_icon, filename, user_designation, user_description, about,
                useridname, password, phone, email, address, department, experience, specialization, totalClasses,
                attendedClasses, Topic1, Topic2, award, hobbies, favoriteTopic)

    updated_user = get_user(user_id)
    updated_user['_id'] = str(updated_user['_id'])

    return jsonify(updated_user)


# TeachEr =End======================================================


# Parents Stat======================================================


@app.route('/parent')
def homeparent():
    return render_template('parent/index.html')


# #get profile by userid
@app.route('/parent/get_parent_data/<string:search_value>', methods=['GET'])
def fetch_parent_data(search_value):
    parent = get_parent(search_value)

    if parent:
        # Modify this part to select the specific fields you want to return
        parent_info = {
            "parent_name": parent.get("parent_name", ""),
            "parent_age": parent.get("parent_age", ""),
            "parent_gender": parent.get("parent_gender", ""),
            "parent_designation": parent.get("parent_designation", ""),
            "parent_description": parent.get("parent_description", ""),
            "parent_email": parent.get("personal_info", {}).get("contact", {}).get("parent_email", "")
        }
        return jsonify(parent_info)
    else:
        return jsonify({'error': 'User does not exist'}), 404





#get_parent_profile
@app.route('/parent/get_parent_profile', methods=['GET','POST'])
def get_parent_profile():
    if request.method == 'GET':
        # Render the 'fetch.html' template when it's a GET request
        return render_template("parent/fetch.html")
    

    parent_useridname = request.form.get("parent_useridname", '')
    parent_password = request.form.get("parent_password", '')
    print(parent_useridname,parent_password)

    session['parent_useridname'] = parent_useridname
    session_parent_useridname = session.get('parent_useridname', '')

    parent = get_parent_by_password_and_useridname(parent_password, parent_useridname)
    print(parent)

    #fetch child data
    # child_data=get_student_data_by_parent_useridname(parent_useridname)

    if parent:
        parent_info = {
            "parent_useridname": parent["parent_useridname"],
        "parent_hashed_password": parent["parent_hashed_password"],
        "parent_name": parent["parent_name"],
        "parent_age": parent["parent_age"],
        "parent_gender": parent["parent_gender"],
        "parent_image": parent["parent_image"],
        "parent_designation": parent["parent_designation"],
        "parent_description": parent["parent_description"],
        "parent_about": parent["personal_info"]["parent_about"],
        "parent_phone": parent["personal_info"]["contact"]["parent_phone"],
        "parent_email": parent["personal_info"]["contact"]["parent_email"],
        "parent_address": parent["personal_info"]["contact"]["parent_address"],
        # "child_name":child_data['student_name'],
        # "child_image":child_data["student_image"]
        }
        return jsonify(parent_info)
    else:
        return jsonify({'error': 'User does not exist'}), 404


#create parent profile
@app.route('/parent/create_parent_profile', methods=['GET', 'POST'])
def create_parent_profile():
    try:
        parent_useridname=request.form.get("parent_useridname", '')
        parent_password=request.form.get("parent_password", '')
        parent_name = request.form.get('parent_name', '')
        parent_designation = request.form.get('parent_designation', '')
        parent_age = request.form.get('parent_age', '')
        parent_gender = request.form.get('parent_gender', '')
        
        parent_description = request.form.get('parent_description', '')
        parent_about = request.form.get('parent_about', '')
        parent_phone = request.form.get('parent_phone', '')
        parent_email = request.form.get('parent_email', '')
        parent_StreetAddress = request.form.get('parent_StreetAddress', '')
        parent_city=request.form.get('parent_city', '')
        parent_PostalCode=request.form.get('parent_PostalCode', '')
        parent_country=request.form.get('parent_country', '')
        parent_Apartment=request.form.get('parent_country', '')
        parent_state=request.form.get('parent_state', '')

        parent_image = request.files['file']
        data=get_parents()
        parent_hashed_password = generate_password_hash(parent_password)
        
        if parent_image:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(parent_image.filename))
            parent_image.save(filename)

        email_exists = any(item['personal_info']['contact']['parent_email'] == parent_email for item in data)
        phone_exists = any(item['personal_info']['contact']['parent_phone'] == parent_phone for item in data)
        useridname=any(item['parent_useridname'] == parent_useridname for item in data)

        if email_exists:
              return jsonify({"message": "This email is already exist"}), 400
        if phone_exists:
              return jsonify({"message": "This phone number is already exist"}), 400
        if useridname:
              return jsonify({"message": "This useridname is already exist"}), 400
        else:
            create_parent(parent_useridname,parent_hashed_password,parent_name, filename, parent_designation, parent_description, parent_about, parent_phone, parent_email, parent_StreetAddress,parent_age,parent_gender,parent_city,parent_PostalCode,parent_country,parent_Apartment,parent_state)

        return jsonify({"message": "Parent profile created successfully"}), 200
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500



#update parent info
@app.route('/parent/update_parent/<string:useridname>', methods=['PUT', 'POST'])
def update_parent_profile(useridname):
    parent_data = get_parent(useridname)
    print(parent_data)
    if not parent_data:
        return jsonify({"error": "Parent not found"}), 404
    # Update parent information based on the received data

    # Example: Update the 'parent_name', 'parent_designation', and 'parent_description'
    parent_data['parent_useridname'] = request.form.get('parent_useridname', parent_data['parent_useridname'])
    parent_data['parent_name'] = request.form.get('parent_name', parent_data['parent_name'])
    parent_data['parent_designation'] = request.form.get('parent_designation', parent_data['parent_designation'])
    parent_data['parent_description'] = request.form.get('parent_description', parent_data['parent_description'])
    parent_data['parent_age'] = request.form.get('parent_age', parent_data['parent_age'])
    parent_data['parent_gender'] = request.form.get('parent_gender', parent_data['parent_gender'])
    # Example: Update the 'parent_about', 'parent_phone', 'parent_email', and 'parent_address' within 'personal_info'
    parent_data['personal_info']['parent_about'] = request.form.get('parent_about', parent_data['personal_info']['parent_about'])
    parent_data['personal_info']['contact']['parent_phone'] = request.form.get('parent_phone', parent_data['personal_info']['contact']['parent_phone'])
    parent_data['personal_info']['contact']['parent_email'] = request.form.get('parent_email', parent_data['personal_info']['contact']['parent_email'])


    parent_data['personal_info']['contact']['parent_address']['parent_country'] = request.form.get('parent_country', parent_data['personal_info']['contact']['parent_address']['parent_country'])

    parent_data['personal_info']['contact']['parent_address']['parent_state'] = request.form.get('parent_state', parent_data['personal_info']['contact']['parent_address']['parent_state'])

    parent_data['personal_info']['contact']['parent_address']['parent_city'] = request.form.get('parent_city', parent_data['personal_info']['contact']['parent_address']['parent_city'])

    parent_data['personal_info']['contact']['parent_address']['parent_StreetAddress'] = request.form.get('parent_StreetAddress', parent_data['personal_info']['contact']['parent_address']['parent_StreetAddress'])

    parent_data['personal_info']['contact']['parent_address']['parent_Apartment'] = request.form.get('parent_Apartment', parent_data['personal_info']['contact']['parent_address']['parent_Apartment'])

    parent_data['personal_info']['contact']['parent_address']['parent_PostalCode'] = request.form.get('parent_PostalCode', parent_data['personal_info']['contact']['parent_address']['parent_PostalCode'])

    # Example: Handle file uploads 
    parent_image = request.files['file']
    if parent_image:
        filename = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(parent_image.filename))
        parent_image.save(filename)
        parent_data['parent_image'] = filename

     # Update password if provided
    new_password = request.form.get('new_password')
    if new_password:
        # You may want to add validation and hashing here
        parent_data['parent_hashed_password'] = generate_password_hash(new_password)

    # Save the updated parent data 
    update_parent(parent_data)

    return jsonify({"message": "Parent information updated successfully"}), 200

# Parents End======================================================


if __name__ == '__main__':
    app.run(debug=True,port=5000)
