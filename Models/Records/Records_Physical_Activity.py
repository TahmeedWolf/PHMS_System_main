from extension import db
from datetime import datetime, timezone

class Records_Physical_Activity(db.Model):
    __tablename__ = 'records_physical_activity'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    activity_type = db.Column(db.String(100))
    duration_minute = db.Column(db.Integer)
    intensity = db.Column(db.String(100))

    # Child relationship to users
    data_activity =  db.relationship("Users", back_populates="user_activity")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

    def __setitem__(self, key, value):
        setattr(self, key, value)