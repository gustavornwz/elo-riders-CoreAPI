# core-api/src/models.py

from datetime import datetime, date
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema, validate
import enum

# db setup
db = SQLAlchemy()

# Users
class Gender(enum.Enum):
    MALE = 1
    FEMALE = 2
    OTHER = 3
    
class Profile(enum.Enum):
    BIKER = 1
    SELLER = 2
    ADMIN = 3

class MembershipLevel(enum.Enum):
    BASIC = 1
    INTERMEDIATE = 2
    ADVANCED =3
    NO = 4
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    lastname = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.Enum(Gender), nullable=False)
    profile = db.Column(db.Enum(Profile), nullable=False)
    membership_level = db.Column(db.Enum(MembershipLevel), nullable=True, default=MembershipLevel.NO)
    phone = db.Column(db.String(120), nullable=False)
    birthdate = db.Column(db.Date, nullable=True)
    elo_score = db.Column(db.Float, default=30.0)
    last_elo_update = db.Column(db.DateTime)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)

class UserSensorData(db.Model):
    __tablename__ = 'user_sensor_data'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Bike IoT data
    last_month_miles = db.Column(db.Float)
    total_miles = db.Column(db.Float)
    avg_speed = db.Column(db.Float)
    braking_events = db.Column(db.Integer)
    
    # User biometric data
    heart_rate = db.Column(db.Integer)
    blood_pressure = db.Column(db.Integer)
    stress_level = db.Column(db.Integer)
    sleep_quality = db.Column(db.Integer)  # Scale 1-10

    # location data
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    user = db.relationship('User', backref=db.backref('sensor_data', lazy=True))

# Serializations
# Enumerations table
class EnumToDict(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {'key':value.name, 'value':value.value}

# Users
class LocationSchema(Schema):
    title = fields.Str(attribute="name")
    coordinates = fields.Dict(attribute=lambda obj: {
        "latitude": obj.latitude,
        "longitude": obj.longitude
    })

class UserSchema(SQLAlchemyAutoSchema):
    gender = EnumToDict(attribute="gender")
    profile = EnumToDict(attribute="profile")
    membership_level = EnumToDict(attribute="membership_level")
    elo_score = fields.Float()
    location = fields.Method("get_user_location")

    def get_user_location(self, obj):
        last_data = UserSensorData.query.filter_by(
            user_id=obj.id
        ).order_by(UserSensorData.timestamp.desc()).first()
        
        if last_data and last_data.latitude and last_data.longitude:
            return {
                "title": obj.name or obj.username,
                "coordinates": {
                    "latitude": last_data.latitude,
                    "longitude": last_data.longitude
                }
            }
        return None

    class Meta:
        model = User
        exclude = ("password",)
        include_relationships = True
        load_instance = True

class UserSensorDataSchema(SQLAlchemyAutoSchema):
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))

    class Meta:
        model = UserSensorData
        include_relationships = True
        load_instance = True

# Validations
class ValidateUserSchemaValidation(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)

class UserSensorDataSchema(Schema):
    user_id = fields.Int(required=True)
    last_month_miles = fields.Float(required=True)
    total_miles = fields.Float(required=True)
    avg_speed = fields.Float(validate=validate.Range(min=0))
    braking_events = fields.Int(validate=validate.Range(min=0))
    heart_rate = fields.Int(validate=validate.Range(min=40, max=220))
    stress_level = fields.Int(validate=validate.Range(min=0, max=100))
    sleep_quality = fields.Int(validate=validate.Range(min=0, max=10))
    latitude = fields.Float(required=True, validate=validate.Range(min=-90, max=90))
    longitude = fields.Float(required=True, validate=validate.Range(min=-180, max=180))