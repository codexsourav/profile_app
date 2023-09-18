from bson import ObjectId
from pymongo import MongoClient

client = MongoClient('mongodb+srv://sourav:sourav@cluster0.6aannpk.mongodb.net')
profile_db = client.get_database('ProfileApp')

profile_collection = profile_db.get_collection('teacherProfile')

def create_user(username,language,call_icon, message_icon, user_image, user_designation, user_description, about, useridname, password, phone, email, address
                ,department, experience, specialization,totalClasses,attendedClasses,Topic1,Topic2,award,
                    hobbies,favoriteTopic):
    user = profile_collection.insert_one({
        'username': username,
        # 'user_class': user_class,
        'language':language,
        'call_icon':call_icon,
        'message_icon':message_icon,
        'user_image': user_image,

        'personal_info': {
            'status':{
                'user_designation': user_designation,
                'user_description': user_description
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

        },
        'academic': {
            'department': department,
            'experience': experience,
            'specialization': specialization,

        },
        'attendence': {
            'totalClasses': totalClasses,
            'attendedClasses': attendedClasses,
        },
        'performance':{
            'classGrades': {
                'topic1': Topic1,
                'topic2': Topic2
            },
            'award':award
        },
        'interest':{
            'hobbies': hobbies,
            'favoriteTopic': favoriteTopic,
        }
    }).inserted_id
    return user

def get_user(user_id):
    # Convert the user_id to ObjectId
    user_id = ObjectId(user_id)
    
    user = profile_collection.find_one({'_id': user_id})
    
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to a string
    
    return user

def update_user(user_id, username, language, call_icon, message_icon, user_image, user_designation, user_description, about,
                useridname, password, phone, email, address, department, experience, specialization, totalClasses,
                attendedClasses, Topic1, Topic2, award, hobbies, favoriteTopic):
    
    profile_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {
            'username': username,
            'language':language,
            'call_icon':call_icon,
            'message_icon':message_icon,

            # 'user_class': user_class,
            'user_image': filename,
            'personal_info': {
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
            },
            
            'academic': {
                'department': department,
                'experience': experience,
                'specialization': specialization,
            },
            'attendence': {
                'totalClasses': totalClasses,
                'attendedClasses': attendedClasses,
            },
            'performance':{
                'classGrades': {
                    'topic1': Topic1,
                    'topic2': Topic2
                    },
                'award':award
            },
            'interest':{
                'hobbies': hobbies,
                'favoriteTopic': favoriteTopic,
            }
        }}
    )



# def get_users():
#     return list(profile_collection.find({}))

