from extension import db
from datetime import datetime, timezone

class Records_Food_Intake(db.Model):
    __tablename__ = 'records_food_intake'
    food_entry_id = db.Column(db.String(100), primary_key=True)
    timestamp = db.Column(db.String(100), default=datetime.now(timezone.utc))
    meal_type = db.Column(db.String(100))
    food_items = db.Column(db.String(100))
    calories = db.Column(db.Integer)
    carbohydrates = db.Column(db.Float)

    # Child relationship to users
    data_food_intake =  db.relationship("Users", back_populates="user_food_intake")
    user_id = db.Column(db.String(100), db.ForeignKey("users.user_id"))