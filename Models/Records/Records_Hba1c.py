from extension import db
from datetime import datetime, timezone

class Records_Hba1c(db.Model):
    __tablename__ = 'records_hba1c'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    hba1c = db.Column(db.Float)

    # Child relationship to users
    data_hba1c =  db.relationship("Users", back_populates="user_hba1c")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_value(self):
        return self.hba1c