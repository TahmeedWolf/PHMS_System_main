from extension import db
from datetime import datetime, timezone

class Records_Glucose_Monitoring(db.Model):
    __tablename__ = 'records_glucose_monitoring'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    glucose_level = db.Column(db.Integer)
    device_id = db.Column(db.String(100))

    # Child relationship to users
    data_cgm =  db.relationship("Users", back_populates="user_cgm")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def get_value(self):
        return self.glucose_level

    def get_timestamp(self):
        return self.timestamp