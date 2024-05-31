from extension import db
from datetime import datetime

class Access_Log(db.Model):
    __tablename__ = "access_logs"
    access_logs_id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.String(100), default=datetime.utcnow())
    user_id = db.Column(db.Integer)
    user_agent = db.Column(db.String(300))
    ip = db.Column(db.String(50))
    verb = db.Column(db.String(10))
    what = db.Column(db.String(200))
    # Child Relationship to Users
    user_access = db.relationship("Users", back_populates="access_log")
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))