from setup_db import *
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from uuid import uuid1
from time import sleep

# Create a hashed password "password"
hash_and_salted_password = generate_password_hash(
        "password",
        method='pbkdf2:sha256',
        salt_length=8
)
user_id=uuid1()
patient001 = Users(user_id=user_id, name_first="Patient001", name_last="LUMI", email="patient001@gmail.com", password=hash_and_salted_password, permission="user")
with app.app_context():
    db.session.add(patient001)
    db.session.commit()

sleep(1) #to prevent 2 exactly same uuid
data_glucose1 = Data_Glucoses(data_glucose_id=uuid1(), data_glucose=10.5, data_timestamp='2014-10-01T19:24', user_id=user_id)
sleep(1) #to prevent 2 exactly same uuid
data_glucose2 = Data_Glucoses(data_glucose_id=uuid1(), data_glucose=11.5, data_timestamp='2014-10-01T19:29', user_id=user_id)

with app.app_context():
    db.session.add(data_glucose1)
    db.session.add(data_glucose2)
    db.session.commit()
