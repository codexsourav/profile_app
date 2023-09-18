from bson import ObjectId
from pymongo import MongoClient
from werkzeug .security import generate_password_hash,check_password_hash
client = MongoClient('mongodb+srv://sourav:sourav@cluster0.6aannpk.mongodb.net/')
profile_db = client.get_database('ParentProfileApp')

profile_collection = profile_db.get_collection('profile')



# save parent info in database
def create_parent(parent_useridname,parent_hashed_password,parent_name, filename, parent_designation, parent_description, parent_about, parent_phone, parent_email, parent_StreetAddress,parent_city,parent_PostalCode,parent_country,parent_Apartment,parent_state,parent_age,parent_gender):
    profile_collection.create_index([('parent_useridname', 1)], unique=True)
    profile_collection.create_index([('personal_info.contact.parent_email', 1)], unique=True)
    profile_collection.create_index([('personal_info.contact.parent_phone', 1)], unique=True)
    parent = profile_collection.insert_one({
        "parent_useridname":parent_useridname,
        "parent_hashed_password":parent_hashed_password,
        'parent_name': parent_name,
        "parent_age":parent_age,
        "parent_gender":parent_gender,
        'parent_image': filename,
        'parent_designation': parent_designation,
        'parent_description': parent_description,
        'personal_info': {
            'parent_about': parent_about,
            'contact': {
                'parent_phone': parent_phone,
                'parent_email': parent_email,
                'parent_address': {"parent_country":parent_country,
                                   "parent_state":parent_state,
                                   "parent_city":parent_city,
                                   "parent_StreetAddress":parent_StreetAddress,
                                   "parent_Apartment":parent_Apartment,
                                   "parent_PostalCode":parent_PostalCode


                                   }
            }
        }
    })
    return parent


#get allparent info
def get_parents():
    return list(profile_collection.find({}))


#get parent by id
def get_parent_by_password_and_useridname(password, useridname):
    parent = profile_collection.find_one({'parent_useridname': useridname})
    if parent:
        stored_password = parent.get('parent_hashed_password', '')
        realpass=check_password_hash(stored_password, password)
        if realpass:
            return parent
    print("db",parent)
    return None


def get_parent(search_value):
    parent = profile_collection.find_one({'parent_useridname': search_value})
    if not parent:
        parent = profile_collection.find_one({'personal_info.contact.parent_email': search_value})
    if not parent:
        parent = profile_collection.find_one({'personal_info.contact.parent_phone': search_value})
    
    return parent





#update parent info
def update_parent(parent_data):
    # Update the parent document in the MongoDB collection based on its ObjectId
    profile_collection.update_one(
        {'_id': ObjectId(parent_data['_id'])},
        {'$set': parent_data}
    )




# get child datta by parent userid
# def get_student_data_by_parent_useridname(parent_useridname):
#     try:
#         # Search for a student with the given parent_useridname
#         student = student_collection.find_one({'parent_useridname': parent_useridname})

#         if student:
#             return student
#         else:
#             return None
#     except Exception as e:
#         # Handle exceptions (e.g., database errors)
#         print(f"Error: {str(e)}")
#         return None




 


