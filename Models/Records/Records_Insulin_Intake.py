from extension import db
from datetime import datetime, timezone

class Records_Insulin_Intake(db.Model):
    __tablename__ = 'records_insulin_intake'
    insulin_entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    insulin_type = db.Column(db.String(100))
    dose = db.Column(db.Integer)

    # Child relationship to users
    data_insulin =  db.relationship("Users", back_populates="user_insulin")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))