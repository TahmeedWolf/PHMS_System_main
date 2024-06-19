from extension import db
from datetime import datetime, timezone
from sqlalchemy.dialects.mysql import BLOB

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    birthday = db.Column(db.String(100))
    gender = db.Column(db.String(12))
    active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(1000), default="default")
    created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    modified_time = db.Column(db.String(100), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    height = db.Column(db.Float)
    health_status = db.Column(db.String(30), default="healthy")
    permission = db.Column(db.String(30), default="user")
    # profile_image = db.Column(BLOB)
    profile_img_url = db.Column(db.String(100))
    # Parent relationship to user_raw (only for doctor)
    user_raw = db.relationship('User_Raw', back_populates="user_raw_record")
    # Parent relationship to records_weight_tracking
    user_weight = db.relationship('Records_Weight_Tracking', back_populates="data_weight")
    # Parent relationship to records_cholesterol
    user_cholesterol = db.relationship('Records_Cholesterol', back_populates="data_cholesterol")
    # Parent relationship to records_hba1c
    user_hba1c = db.relationship('Records_Hba1C', back_populates="data_hba1c")
    # Parent relationship to records_hba1c
    user_bp = db.relationship('Records_Blood_Pressure', back_populates="data_bp")
    # Parent relationship to records_food_intake
    user_food_intake = db.relationship('Records_Food_Intake', back_populates="data_food_intake")
    # Parent relationship to records_insulin
    user_insulin = db.relationship('Records_Insulin_Intake', back_populates="data_insulin")
    # Parent relationship to records_activity
    user_activity = db.relationship('Records_Physical_Activity', back_populates="data_activity")
    # Parent relationship to records_cgm
    user_cgm = db.relationship('Records_Glucose_Monitoring', back_populates="data_cgm")
    # Parent relationship to Access Logs
    access_log = db.relationship('Access_Log', back_populates="user_access")

    def get_id(self):
            return (self.user_id)

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary   

class User_Raw(db.Model):
    __tablename__ = 'user_raw'
    user_raw_id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String)
    license_number = db.Column(db.String)
    address = db.Column(db.String)
    h_organisation_id = db.Column(db.String(100))

    # Child relationship to users
    user_raw_record = db.relationship('Users', back_populates="user_raw")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))
