# This file is for setup of database (recreate all tables)
# Run in virtual environment by $ python __filename__
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as text
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
from sqlalchemy.dialects.mysql import BLOB

# Load all env and initiate the app
load_dotenv()
app = Flask("app")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.secret_key = os.environ.get('APP_SECRET_KEY')
db = SQLAlchemy()
db.init_app(app)

class Healthcare_Organisations(db.Model):
    __tablename__ = 'healthcare_organisations'
    organisation_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    address = db.Column(db.String(200))
    profile_img_url = db.Column(db.String(100))
    # Parent relationship with Healthcare_Providers
    # provider = db.relationship('Healthcare_Providers', back_populates="organisation")
    # TODO: add healthcare provider raw then link to this

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    birthday = db.Column(db.String(100), default=datetime.now(timezone.utc))
    gender = db.Column(db.String(12))
    # medical_history = db.Column(db.String) # what is this # TODO: move this to visit / history / another table
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(1000), default="default")
    created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    modified_time = db.Column(db.String(100), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    profile_image = db.Column(BLOB)
    permission = db.Column(db.String(30), default="user")
    Parent relationship to Glucose Readings
    data_glucose = db.relationship('xx', back_populates="xx")
    Parent relationship to Care_Patient_Providers (Patient)
    care = db.relationship('Care_Patient_Providers', back_populates="care_patient")
    # Parent relationship to Care_Patient_Providers (Doctor)
    care_hp = db.relationship('Care_Patient_Providers', back_populates="care_provider")
    # Parent relationship to Care_Patient_Providers
    visit = db.relationship('Visits', back_populates="visit_patient")
    # Parent relationship to Care_Patient_Providers
    visit_hp = db.relationship('Visits', back_populates="visit_hp")
    # Parent relationship to Access_logs
    user_access = db.relationship('Access_logs', back_populates="access_logs")


# Done
# class Care_Patient_Providers(db.Model):
#     __tablename__ = 'care_patient_providers'
#     id = db.Column(db.Integer, primary_key=True)
#     # Child relationship to Users 'Patients' (2)
#     care_patient = db.relationship('Users', back_populates="care")
#     patient_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

#     # Child relationship to Users 'Healthcare_Providers' (2)
#     care_provider = db.relationship('Users', back_populates="care_hp")
#     healthcare_provider_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))


# class Visits(db.Model):
#     __tablename__ = 'visits'
#     id = db.Column(db.Integer, primary_key=True)
#     visit_timestamp = db.Column(db.String(100))
#     diagnosis = db.Column(db.String(200))
#     physician_notes = db.Column(db.String(500))
#     # Child relationship to Patients (2)
#     visit_patient = db.relationship('Users', back_populates="visit")
#     patient_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))
#     # Child relationship to HP (2)
#     visit_hp = db.relationship('Users', back_populates="visit_hp")
#     hp_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

# class Access_logs(db.Model):
#     __tablename__ = "access_log"
#     access_log_id = db.Column(db.Integer, primary_key=True)
#     access_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
#     user_agent = db.Column(db.String(300))
#     ip = db.Column(db.String(50))
#     verb = db.Column(db.String(10))
#     what = db.Column(db.String(200))
#     # Child Relationship to Users
#     access_logs = db.relationship("Patients", back_populates="user_access")
#     user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

# class Message_logs(db.Model):
#     __tablename__ = "message_logs"
#     message_id = db.Column(db.Integer, primary_key=True)
#     created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
#     active = db.Column(db.Boolean, default=True)
    

# class Data_Glucoses(db.Model):
#     __tablename__ = 'data_glucoses'
#     data_glucose_id = db.Column(db.String(100), primary_key=True)
#     created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
#     data_timestamp = db.Column(db.String(100))
#     data_glucose = db.Column(db.Float)
#     # Child Relationship to Users
#     user = db.relationship("Users", back_populates="data_glucose")
#     user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

print("successfully completed.")

if __name__ == "__main__":
    # Only execute this when it is run as a script (called from terminal)
    with app.app_context():
        db.create_all()
