from extension import db
from datetime import datetime, timezone
from uuid import uuid1

class Records_Food_Intake(db.Model):
    __tablename__ = 'records_food_intake'
    entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    meal_type = db.Column(db.String(100))
    food_items = db.Column(db.String(100))
    calories = db.Column(db.Integer)
    carbohydrates = db.Column(db.Float)

    # Child relationship to users
    data_food_intake =  db.relationship("Users", back_populates="user_food_intake")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get_timestamp(self):
        return self.timestamp

    def get_value(self):
        return self.food_items