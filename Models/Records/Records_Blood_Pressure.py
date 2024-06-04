from extension import db
from datetime import datetime, timezone

class Records_Blood_Pressure(db.Model):
    __tablename__ = 'records_blood_pressure'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    systolic = db.Column(db.Integer)
    diastolic = db.Column(db.Integer)

    # Child relationship to users
    data_bp =  db.relationship("Users", back_populates="user_bp")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

    def __setitem__(self, key, value):
        setattr(self, key, value)