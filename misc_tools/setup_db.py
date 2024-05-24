# This file is for setup of database (recreate all tables)
# Run in virtual environment by $ python __filename__
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as text
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

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
    # Parent relationship with Healthcare_Providers
    provider = db.relationship('Healthcare_Providers', back_populates="organisation")

class Healthcare_Providers(db.Model):
    __tablename__ = 'healthcare_providers'
    healthcare_provider_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(100))
    created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    permission=db.Column(db.String(64), default="healthcare_provider")
    designation=db.Column(db.String(64))
    qualification=db.Column(db.String(64))
    license_number=db.Column(db.String(64))
    address=db.Column(db.String(200))
    # Child relationship with Healthcare_Organisations
    provider = db.relationship('Healthcare_Organisations', back_populates="provider")
    organisation_id = db.Column(db.String(100), db.ForeignKey("healthcare_organisations.organisation_id"))
    # Parent relationship with Care_Patient_Providers
    care = db.relationship('Care_Patient_Providers', back_populates="care_provider")
    # Parent relationship to Care_Patient_Providers
    visit = db.relationship('Visits', back_populates="visit_provider")
    # Parent relationship to Access_logs
    provider_access = db.relationship('Access_logs', back_populates="access_logs")


class Patients(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    birthday = db.Column(db.String(100), default=datetime.now(timezone.utc)) # TODO:CHECK
    gender = db.Column(db.String(12))
    medical_history = db.Column(db.String) # what is this
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(1000), default="default")
    created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    modified_time = db.Column(db.String(100), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    profile_pic = db.Column(db.String)
    # Parent relationship to Glucose Readings
    # data_glucose = db.relationship('xx', back_populates="xx")
    # Parent relationship to Care_Patient_Providers
    care = db.relationship('Care_Patient_Providers', back_populates="care_patient")
    # Parent relationship to Care_Patient_Providers
    visit = db.relationship('Visits', back_populates="visit_patient")
    # Parent relationship to Access_logs
    patient_access = db.relationship('Access_logs', back_populates="access_logs")



class Care_Patient_Providers(db.Model):
    __tablename__ = 'care_patient_providers'
    id = db.Column(db.Integer, primary_key=True)
    # Child relationship to Patients (2)
    care_patient = db.relationship('Patients', back_populates="care")
    patient_id = db.Column(db.String(100), db.ForeignKey("patients.patient_id"))

    # Child relationship to Healthcare_Providers (2)
    care_provider = db.relationship('Healthcare_Providers', back_populates="care")
    provider_id = db.Column(db.String(100), db.ForeignKey("healthcare_providers.healthcare_provider_id"))

class Visits(db.Model):
    __tablename__ = 'visits'
    id = db.Column(db.Integer, primary_key=True)
    visit_timestamp = db.Column(db.String(100))
    diagnosis = db.Column(db.String(200))
    physician_notes = db.Column(db.String(500))
    # Child relationship to Patients (2)
    visit_patient = db.relationship('Patients', back_populates="visit")
    patient_id = db.Column(db.String(100), db.ForeignKey("patients.patient_id"))

    # Child relationship to Healthcare_Providers (2)
    visit_provider = db.relationship('Healthcare_Providers', back_populates="visit")
    provider_id = db.Column(db.String(100), db.ForeignKey("healthcare_providers.healthcare_provider_id"))

class Access_logs(db.Model):
    __tablename__ = "access_log"
    access_log_id = db.Column(db.Integer, primary_key=True)
    access_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    user_agent = db.Column(db.String(300))
    ip = db.Column(db.String(50))
    verb = db.Column(db.String(10))
    what = db.Column(db.String(200))
    # Child Relationship to Patient
    access_logs = db.relationship("Patients", back_populates="patient_access")
    patient_id = db.Column(db.String(100), db.ForeignKey("patients.patient_id"))
    # Child Relationship to H.Providers
    access_logs = db.relationship("Healthcare_Providers", back_populates="provider_access")
    provider_id = db.Column(db.String(100), db.ForeignKey("providers.healthcare_provider_id"))

class Message_logs(db.Model):
    __tablename__ = "message_logs"
    message_id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    active = db.Column(db.Boolean, default=True)
    # weird... how do we do this? provider and patient?



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
