from extension import db
from datetime import datetime, timezone

class Records_Cholesterol(db.Model):
    __tablename__ = 'records_cholesterol'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    total_cholesterol = db.Column(db.Integer)
    hdl = db.Column(db.String(100))
    ldl = db.Column(db.String(100))
    triglycerides = db.Column(db.Integer)
    # Child relationship to users
    data_cholesterol =  db.relationship("Users", back_populates="user_cholesterol")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

    def __setitem__(self, key, value):
        setattr(self, key, value)