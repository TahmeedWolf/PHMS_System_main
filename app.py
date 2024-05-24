from flask import Flask, request, render_template, flash, url_for, redirect, Response
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sqlalchemy import text
from werkzeug.utils import secure_filename
from time import sleep
import json
from uuid import uuid1
import pandas as pd
from integrations.kg_engine.neo4j_tools import *
from integrations.nlg.MessageAnalyzer import MessangeAnalyzer
from flask_bootstrap import Bootstrap5

# Models
from Models.Users import *

# Security
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user

# Load environment variables from .env file
load_dotenv()
NEO4J_DB_URI = os.environ.get('NEO4J_DB_URI')
NEO4JDB_USER = os.environ.get('NEO4JDB_USER')
NEO4JDB_PASSWORD = os.environ.get('NEO4JDB_PASSWORD')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.secret_key = os.environ.get('APP_SECRET_KEY')
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
# app.config['UPLOAD_FOLDER'] = 'uploads/'

URI = f"neo4j+s://{NEO4J_DB_URI}"
AUTH = (NEO4JDB_USER, NEO4JDB_PASSWORD)

from extension import db
db.init_app(app)

bootstrap = Bootstrap5(app)

def execute_query(driver, query, query_detail="", database="neo4j"):
  if query_detail !="":
    summary = driver.execute_query(
        query,
        database_=database,
    ).summary
    print("Created {nodes_created} nodes in {time} ms.".format(
        nodes_created=summary.counters.nodes_created,
        time=summary.result_available_after
    ))
  else:
    summary = driver.execute_query(
        query,
        query_detail,
        database_=database,
    ).summary
    print("Created {nodes_created} nodes in {time} ms.".format(
        nodes_created=summary.counters.nodes_created,
        time=summary.result_available_after
    ))
  return 'Success'

@app.route('/')
@login_required
def home():
    return render_template('home/dashboard.html')

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    
    return db.get_or_404(Users, user_id)


# Redirect to login when user is not logged in (with default message)
login_manager.login_view = "login"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        # Locate user by email entered.
        user = Users.query.where(text(f"users.email='{email}'")).first()
        print(user.name)
        print(user.is_active)
        # Email doesn't exist or password incorrect
        if not user:
            flash("That email does not exist. Please try again.")
            return redirect(url_for('login'))
        # Check stored password hash against entered password hashed.
        elif not check_password_hash(user.password, password):
            flash("Password incorrect. Please try again.")
            return redirect(url_for('login'))
        elif user.is_active == 0:
            flash("This account is no longer active.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('home/login.html')

@app.route('/logout')
@login_required
# @access_log
def logout():
    logout_user()
    logout_message = "You have been logged out successfully."
    flash(logout_message)
    return redirect(url_for("login"))



@app.route('/test_neo4j')
def get_neo4j():

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        records, summary, keys = driver.execute_query(
            """MATCH (p:Patient) return p;""",
            database_="neo4j",
        )

        # Loop through results and do something with them
        for record in records:
            print(record.data())  # obtain record as dict
        return str(records[0].data())

@app.route('/test_postgreql')
def get_postgreql():
   query = 'SELECT * FROM users limit 1;'
   users = db.session.execute(text(query)).all()
   print(users)
   return str(users)

@app.route('/test_mysql')
def get_mysql():
   query = 'SELECT * from users u;'
   users = db.session.execute(text(query)).fetchall()
   return str(users)

@app.route('/test_openai')
def get_openai():
   analyzer = MessangeAnalyzer('English')
   analyzer_response = analyzer.evaluate("2024-05-11T00:38:21.439536 Dinner Salt, Tofu, Spices 2024-05-09T21:29:21.439536 Dinner Herbs, Salt, Lentils 2024-05-09T10:36:21.439536 Lunch Chicken breast, Cereal, Lentils, Soy sauce 2024-05-07T18:37:21.439536 Dinner Beans, Strawberries, Tofu 2024-05-06T20:21:21.439536 Dinner Mayonnaise, Tuna, Oats 2024-05-05T21:26:21.439536 Lunch Raspberries, Herbs, Maple syrup, Beans, Oats 2024-05-05T13:54:21.439536 Dinner Cucumber, Eggs, Carrot 2024-05-11T08:32:21.219779 104 2024-05-10T07:56:21.219779 96 2024-05-08T17:46:21.219779 98 2024-05-08T05:43:21.219779 158 2024-05-07T08:09:21.219779 161 2024-05-06T03:51:21.219779 171 2024-05-05T00:20:21.219779 193")

   return analyzer_response

@app.route('/upload_files', methods=['GET','POST'])
def route_upload_files():
   if request.method == "GET":
       return render_template("upload_file.html")
   elif request.method == "POST":
            try:
                f = request.files["file"]
                print(f)
                # filename = secure_filename(f.filename)
                # filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                # f.save(filepath)
                current_user_id = '32f20bb9-0e1e-11ef-b334-28d0ea7c5d57'
                # Save the file in device_warranty_raw
                df = pd.read_excel(f)
                print(len(df))
                print(df.info())

                # for row in range(len(df[:2])):
                #     glucose_id1 = uuid1()
                #     new_data_glucose = Data_Glucoses(data_glucose_id=glucose_id1, data_timestamp=df.iloc[row]['date and time'], data_glucose=df.iloc[row]['glucose'],user_id=current_user_id)
                #     db.session.add(new_data_glucose)
                #     db.session.commit()
                #     sleep(0.2)

                # Status: Inserting of neo4j records
                print('before')
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                create_glucose_data(driver, current_user_id, df[1:10])
                flash(f"{len(df)} records is added successfully!")
                # Reset the file
                request.files["file"] = ""
                return render_template("upload_file.html")
                
            except Exception as e:
                return f"Error: {e.__context__}"
   
# 404-error handler    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('home/page-404.html'), 404

if __name__ == '__main__':
    app.run()