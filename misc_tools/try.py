# This file is for setup of database (recreate all tables)
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from uuid import uuid1
import os

# Load all env and initiate the app
load_dotenv()
db = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URI", None))

# Create a hashed password "password"
hash_and_salted_password = generate_password_hash(
        "password",
        method='pbkdf2:sha256',
        salt_length=8
)

user_id=uuid1()

with open('misc_tools/profile_img.png', 'rb') as file:
    # profile_img = Image.open(file)
    # profile_img=1
    # code = str.encode(file)
    # code = str.encode(tmp)
    tmp = file.read()
    profile_img = bytes.hex(tmp)
    profile_img = "0x"+profile_img
    # print(profile_img)

with db.connect() as connection:
    query = f"""insert
        into
        users (user_id,
        name,
        birthday,
        email,
        password,
        profile_image)
    values ('{user_id}',
        'Peter',
        date('1997-10-11'),
        'peter@gmail.com',
        '{hash_and_salted_password}',
        '{profile_img}');"""
    
    connection.execute(text(query))
    connection.commit()
    connection.close()



# with db.connect() as connection:
#     response = connection.execute(text("select * from users u;")).fetchall()
#     print(response)
#     connection.close()