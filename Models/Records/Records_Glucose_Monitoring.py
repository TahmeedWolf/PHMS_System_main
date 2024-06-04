from extension import db
from datetime import datetime, timezone

class Record_Glucose_Monitoring(db.Model):
    __tablename__ = 'records_glucose_monitoring'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    glucose_level = db.Column(db.Integer)
    device_id = db.Column(db.String(100))
    user_id = db.Column(db.String(100))

    def __setitem__(self, key, value):
        setattr(self, key, value)