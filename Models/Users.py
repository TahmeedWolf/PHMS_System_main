from extension import db
from datetime import datetime, timezone
from sqlalchemy.dialects.mysql import BLOB

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    birthday = db.Column(db.String(100), default=datetime.now(timezone.utc))
    gender = db.Column(db.String(12))
    is_active = db.Column(db.Boolean, default=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(1000), default="default")
    created_time = db.Column(db.String(100), default=datetime.now(timezone.utc))
    modified_time = db.Column(db.String(100), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    profile_image = db.Column(BLOB)
    permission = db.Column(db.String(30), default="user")

    def get_id(self):
            return (self.user_id)

    def is_authenticated(self):
        return True

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary   