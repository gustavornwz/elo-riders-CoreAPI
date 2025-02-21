# core-api/src/user/views.py

import requests, json
from flask import request, Blueprint, jsonify
from marshmallow import ValidationError
from src.models import db, User, UserSchema, ValidateUserSchemaValidation
from src.models import UserSensorData, UserSensorDataSchema
from src.models import Gender, Profile, MembershipLevel
from src.user.elo_service import calculate_elo
from src.user.util import Util
from datetime import datetime, date

# get schemas
user_schema = UserSchema()
sensor_schema = UserSensorDataSchema()

# blueprints
users_blueprint = Blueprint("users", __name__, url_prefix="/users/")
sensor_blueprint = Blueprint("sensors", __name__, url_prefix="/sensors/")
elo_blueprint = Blueprint("elo", __name__, url_prefix="/elo/")

# --- Users ---
# /users/ping (Health check)
@users_blueprint.route('/ping', methods=['GET'])
def ping_user():
    return {"message": "pong", "status": "success"}

# /users/ - "/"
@users_blueprint.route('/', methods=['GET'])
def get_users():
    # if request.method == 'GET':
        return user_schema.dump(User.query.all(), many=True), 200

# /users/friends
@users_blueprint.route('/friends', methods=['GET'])
def get_friends():
    users = User.query.all()
    friends = []
    
    for user in users:
        last_data = UserSensorData.query.filter_by(user_id=user.id).order_by(
            UserSensorData.timestamp.desc()
        ).first()
        
        if last_data and last_data.latitude and last_data.longitude:
            friends.append({
                "title": user.name or user.username,
                "latitude": last_data.latitude,
                "longitude": last_data.longitude
            })
    
    return jsonify(friends), 200

# /users/ - "/"
@users_blueprint.route('/', methods=['POST'])
def post_users():
    # verify that all fields are present
    required_fields = [
        'username', 
        'password', 
        'email', 
        'profile'
        ]

    # Validate required fields
    if not all(field in request.json for field in required_fields):
        return {"message": "Missing required fields", "status": "fail"}, 400

    username=request.json['username']
    password=request.json['password']
    email=request.json['email']
    name= None if 'name' not in request.json else request.json['name']
    lastname = None if 'lastname' not in request.json else request.json['lastname']
    gender = request.json['gender']
    profile = request.json['profile']
    address = None if 'address' not in request.json else request.json['address']
    phone = None if 'phone' not in request.json else request.json['phone']
    membership_level = request.json['membership_level']

    birthdate = request.json.get('birthdate')
    if birthdate:
        try:
            birthdate = datetime.strptime(birthdate, "%Y-%m-%d").date()
        except ValueError:
            return {
                "message": "Invalid birthdate format (YYYY-MM-DD)", 
                "status": "fail"
                }, 400

    if not all([username, password, email, profile]):
        return {
                "message": "All fields are required", 
                "status": "fail"
                }, 400

    new_user = User(username=username,
                    password=Util.salifyHash(password, email),
                    email=email,
                    name=name,
                    lastname=lastname,
                    gender=gender,
                    address=address,
                    phone=phone,
                    profile=profile,
                    birthdate=birthdate,
                    membership_level=membership_level)

    try:
        gender = Gender[request.json['gender'].upper()]
        profile = Profile[request.json['profile'].upper()]
        membership_level = MembershipLevel[request.json['membership_level'].upper()]
    except KeyError as e:
        return {
            "message": f"Valor inválido para {str(e)}", 
            "status": "fail"
            }, 400

    try:
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return {
                "message": "Username or email already exists", 
                "status": "fail"
                }, 412

        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error adding user to DB: {0}".format(e))
        return {
                "message": "Error creando un usuario",
                "status": "error"
                }, 500

    user = user_schema.dump(new_user)

    return {
        "id": user['id'],
        "createdAt": user['createdAt'],
        "username": user['username'],
        "profile": user['profile'],
        "membership_level": user['membership_level']
    }, 201

# /users/user/user_id
@users_blueprint.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {"message": "User not found", "status": "fail"}, 404
    
    last_data = UserSensorData.query.filter_by(user_id=user_id).order_by(
        UserSensorData.timestamp.desc()
    ).first()    

    response = user_schema.dump(user)
    response.update({
        "location": {
            "title": user.name or user.username,
            "coordinates": {
                "latitude": last_data.latitude if last_data else None,
                "longitude": last_data.longitude if last_data else None
            }
        } if last_data else None,
        "elo": user.elo_score
    })
    return response, 200

# /users/user/user_id/elo
@users_blueprint.route('/user/<int:user_id>/elo', methods=['GET'])
def get_user_elo(user_id):
    user = User.query.get(user_id)
    if not user:
        return {
            "message": "User not found", 
            "status": "fail"
            }, 404
    
    return {
        "elo_score": user.elo_score,
        "last_update": user.last_elo_update.isoformat() if user.last_elo_update else None,
        "status": "success"
    }, 200

# /users/user/user_id
@users_blueprint.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return {
             "message": "User not found", 
             "status": "fail"
             }, 404

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Error in DB: {0}".format(e))
        return {
            "message": "Error en BD",
            "status": "error"
        }, 500
    return {"message": "User deleted", "status": "success"}, 200

# /users/login
@users_blueprint.route('/login', methods=['POST'])
def login():
    schema = ValidateUserSchemaValidation()
    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages_dict, 400
    
    user = User.query.filter_by(
        email=request.json['email'],
        password=Util.salifyHash(request.json['password'], request.json['email'])
    ).first()

    if not user:
        return {"message": "Credenciales inválidas", "status": "fail"}, 401

    return {
        "name": f"{user.name} {user.lastname}",
        "elo": float(user.elo_score)
    }, 200

# --- Sensors ---
@sensor_blueprint.route('data', methods=['POST'])
def add_sensor_data():
    """Add sensor data for a user"""
    user_id = request.json.get('user_id')
    if not user_id:
        return {
            "message": "User ID required", 
            "status": "fail"
            }, 400
    
    try:
        new_data = UserSensorData(
            user_id=user_id,
            last_month_miles=request.json.get('last_month_miles'),
            total_miles=request.json.get('total_miles'),
            avg_speed=request.json.get('avg_speed'),
            braking_events=request.json.get('braking_events'),
            heart_rate=request.json.get('heart_rate'),
            blood_pressure=request.json.get('blood_pressure'),
            stress_level=request.json.get('stress_level'),
            sleep_quality=request.json.get('sleep_quality'),
            latitude=request.json.get('latitude'),
            longitude=request.json.get('longitude')
        )
        
        db.session.add(new_data)
        db.session.commit()

        # Update user ELO score
        user = User.query.get(user_id)
        age = Util.calculate_age(user.birthdate)
        
        elo_params = {
            "age": age,
            "last_month_miles": new_data.last_month_miles,
            "total_miles": new_data.total_miles,
            "avg_speed": new_data.avg_speed,
            "braking_events": new_data.braking_events,
            "heart_rate_avg": new_data.heart_rate,
            "stress_level": new_data.stress_level,
            "sleep_quality": new_data.sleep_quality
        }
        
        user.elo_score = calculate_elo(elo_params)
        user.last_elo_update = datetime.utcnow()
        
        db.session.commit()
        
        response_data = sensor_schema.dump(new_data)
        response_data["elo_score"] = user.elo_score

        return response_data, 201
        
    except Exception as e:
        db.session.rollback()
        return {
            "message": str(e), 
            "status": "error"
            }, 500

@sensor_blueprint.route('data/<int:user_id>', methods=['GET'])
def get_sensor_data(user_id):
    """Get sensor data for a user"""
    data = UserSensorData.query.filter_by(user_id=user_id).all()
    return sensor_schema.dump(data, many=True), 200

# --- Elo ---
@elo_blueprint.route('calculate/<int:user_id>', methods=['GET'])
def get_elo(user_id):
    """ELO calculation for a user"""
    try:
        user = User.query.get(user_id)
        sensor_data = UserSensorData.query.filter_by(user_id=user_id).first()

        age = Util.calculate_age(user.birthdate)
        if age is None:
            return {"message": "Fecha de nacimiento requerida", "status": "fail"}, 400
        
        if not user or not sensor_data:
            return {"message": "Datos insuficientes", "status": "fail"}, 404
        
        # Prepare ELO parameters
        elo_params = {
            "age": age,
            "last_month_miles": sensor_data.last_month_miles,
            "total_miles": sensor_data.total_miles,
            "avg_speed": sensor_data.avg_speed,
            "braking_events": sensor_data.braking_events,
            "heart_rate_avg": sensor_data.heart_rate,
            "stress_level": sensor_data.stress_level,
            "sleep_quality": sensor_data.sleep_quality
        }
        print(f'elo_params = {elo_params}')
        
        # Ollama server request
        elo_score = calculate_elo(elo_params)
        
        return {
            "elo_score": elo_score, 
            "status": "success"
            }, 200
        
    except Exception as e:
        return {
            "message": str(e), 
            "status": "error"
            }, 500