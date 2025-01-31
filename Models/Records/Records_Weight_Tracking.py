from extension import db
from datetime import datetime, timezone

class Records_Weight_Tracking(db.Model):
    __tablename__ = 'records_weight_tracking'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    weight = db.Column(db.Float)
    # Child relationship to users
    data_weight =  db.relationship("Users", back_populates="user_weight")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

    def __setitem__(self, key, value):
        setattr(self, key, value)
    
    def get_value(self):
        return self.weight
