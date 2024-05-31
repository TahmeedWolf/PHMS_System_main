from extension import db
from datetime import datetime, timezone

class Notifications(db.Model):
    __tablename__ = 'notification_logs'
    notification_id = db.Column(db.Integer, primary_key=True)
    notification_content = db.Column(db.String)
    created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    active = db.Column(db.Boolean, default=True)
    to_user_id = db.Column(db.String(100))