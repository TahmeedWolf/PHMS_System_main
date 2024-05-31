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

# User profile image
from PIL import Image
import io
import base64

# Models
from Models.Users import *
from Models.Notifications import *
from Models.Authentication import *
# Models.Records
from Models.Records.Records_Cholesterol import *
from Models.Records.Records_Food_Intake import *
from Models.Records.Records_Glucose_Monitoring import *
from Models.Records.Records_Hba1c import *
from Models.Records.Records_Insulin_Intake import *
from Models.Records.Records_Physical_Activity import *
from Models.Records.Records_Weight_Tracking import *

# Security
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from cybersecurity.authentication import *

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
        user = Users.query.where(text(f"users.email='{email}' and users.active=1")).first()
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

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template('home/signup.html')
    elif request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        password_check = request.form.get('password_check')
        username = request.form.get('username')

        # Locate user by email entered.
        user = Users.query.where(text(f"users.email='{email}'")).first()
        # Email exist and the user is active
        if user and int(user.active) ==0:
            flash("Error: A user with this email address already exists. Please login.")
            return redirect(url_for('signup'))
        # Check if two password are the same
        if password != password_check:
            flash("Error: The passwords do not match. Please re-enter your passwords.")
            return redirect(url_for('signup'))

        # hash password
        hash_and_salted_password = generate_password_hash(password,
                                                            method='pbkdf2:sha256',
                                                            salt_length=8)
        new_user_id = uuid1()
        # create the user
        new_user = Users(user_id=new_user_id,name=username, email=email, password=hash_and_salted_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Register successfully. Please login.")
        return redirect(url_for('get_started'))

@app.route('/get_started', methods=["GET","POST"])
@login_required
@access_log
def get_started():
    # Gathering sufficient basic user data for patient (First time login only)
    if request.method == "GET":
        return render_template('settings/get_started.html')
    elif request.method == "POST":
        gender = request.form.get('gender')
        birthday = request.form.get('birthday')
        weight = request.form.get('weight') # in weight record table and kg
        height = request.form.get('height')

        if gender == 'f':
            gender = "Female"
        elif gender == 'm':
            gender = "Male"
        else:
            gender = ''

        # Find the user
        updated_user = Users.query.get(current_user.user_id)
        updated_user.gender = gender
        updated_user.birthday = birthday
        updated_user.height = height

        user_weight_uuid = uuid1()
        user_weight = Records_Weight_Tracking(weight_entry_id=user_weight_uuid, weight=weight,user_id=current_user.user_id)
        db.session.add(user_weight)

        db.session.commit()
        flash("Your basic information has been added successfully.")
        return redirect(url_for("home"))

@app.route('/create_new_hp', methods=["GET","POST"])
@login_required
@access_log
@admin_only
def create_new_hp():
    if request.method == "GET":
        return render_template('users/create_new_hp.html')
    elif request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        password_check = request.form.get('password_check')
        username = request.form.get('username')

        # Locate user by email entered.
        user = Users.query.where(text(f"users.email='{email}'")).first()
        # Email exist and the user is active
        if user and int(user.active) ==0:
            flash("Error: A user with this email address already exists. Please login.")
            return redirect(url_for('create_new_hp'))
        # Check if two password are the same
        if password != password_check:
            flash("Error: The passwords do not match. Please re-enter your passwords.")
            return redirect(url_for('create_new_hp'))

        # hash password
        hash_and_salted_password = generate_password_hash(password,
                                                            method='pbkdf2:sha256',
                                                            salt_length=8)
        new_user_id = uuid1()
        # create the user
        new_user = Users(user_id=new_user_id,name=username, email=email, password=hash_and_salted_password, permission="doctor")
        db.session.add(new_user)
        db.session.commit()

        flash(f"New healthcare provider account {new_user.email} created successfully!")
        return redirect(url_for("create_new_hp"))


@app.route('/logout')
@login_required
# @access_log
def logout():
    logout_user()
    logout_message = "You have been logged out successfully."
    flash(logout_message)
    return redirect(url_for("login"))

@app.route('/')
@login_required
@access_log
def home():
    """Below Shows the basic data format"""
    user_info = {"birthday": "1996-10-11", "gender": "male", "name": "Peter"}
    user_basic = {"height": 170, "weight":72}
    user_notification = """To manage your body weight and blood glucose levels effectively, 
                            focus on balanced meals with high-fiber foods, like beans and vegetables, and lean proteins, 
                            such as tofu and chicken breast. Avoid high sugar and processed foods; instead, 
                            opt for natural ingredients. Regularly monitoring your glucose levels is essential—aim 
                            to keep it within the normal range (70-130 mg/dL before meals and less than 180 
                            mg/dL after meals). Incorporate regular physical activity, such as daily walks or 
                            exercise, to help maintain a healthy weight and improve insulin sensitivity. Stay 
                            hydrated and consult your healthcare provider for personalized advice."""
    user_summary_data = {"cgm": {"record_cgm_latest": 80, "status": "normal"},
                           "hb" : {"record_hb_latest": 98, "status": "normal"},
                           "bp" : {"record_bp_systolic": 102, "record_bp_diastolic": 72, "status": "normal"}
                         }
    user_meal_logs = [
                        ["2024-05-20 18:06:07", "Chicken breast, Milk, Nuts, Cheese, Blueberries","Dinner", 378, 14],
                      ["2024-05-20 12:06:07", "Eggs, Milk","Lunch", 707, 89],
                      ["2024-05-20 08:06:07", "Cheese, Eggs, Mustard, Milk, Maple syrup","Breakfast", 970, 70],
                        ["2024-05-19 18:06:07", "Grapes, Milk, Blueberries, Rice, Apple","Dinner", 378, 14],
                      ["2024-05-19 12:06:07", "Beef, Cucumber","Lunch", 707, 89],
                      ["2024-05-19 08:06:07", "Cheese, Eggs, Mustard, Milk, Maple syrup","Breakfast", 970, 70],
                      ]
    
    user_line_chart_hba1c = [   ["2024-05-14T16:22:34.462354", 9.64],
                                ["2024-05-13T19:13:34.462354", 6.99],
                                ["2024-05-12T19:27:34.462354", 4.44],
                                ["2024-05-11T03:54:34.462354", 5.59],
                                ["2024-05-10T13:29:34.462354", 4.78],
                                ["2024-05-09T19:50:34.462354", 8.13],
                                ["2024-05-08T13:59:34.462354", 4.84]
                            ]
    user_line_chart_weight = [
                                ["2024-05-14T12:29:34.525233", 75.1],
                                ["2024-05-13T18:34:34.525233", 77.8],
                                ["2024-05-13T08:02:34.525233", 76.4],
                                ["2024-05-11T14:13:34.525233", 75.1],
                                ["2024-05-11T04:22:34.525233", 75.7],
                                ["2024-05-09T13:58:34.525233", 75.2],
                                ["2024-05-08T11:47:34.525233", 76]
    ]
    user_line_chart_cgm = [
                                ["2024-05-14T19:14",10.3],
                                ["2024-05-14T19:19",9.9],
                                ["2024-05-14T19:23",9.4],
                                ["2024-05-14T19:24",9.8],
                                ["2024-05-14T19:29",9.6],
                                ["2024-05-14T19:34",9.4],
                                ["2024-05-14T19:39",9.2],
                                ["2024-05-14T19:44",8.9],
                                ["2024-05-14T19:49",8.7],
                                ["2024-05-14T19:54",8.4],
                                ["2024-05-14T19:59",8.2],
                                ["2024-05-14T20:04",8],
                                ["2024-05-14T20:09",7.9],
                                ["2024-05-14T20:14",7.9],
                                ["2024-05-14T20:19",7.8]
                        ]

    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()

    return render_template('home/index.html',
                           user_info=user_info,
                           user_basic=user_basic,
                           user_notifications=user_notifications,
                           user_summary_data=user_summary_data,
                           user_meal_logs=user_meal_logs,
                           user_line_chart_hba1c=user_line_chart_hba1c,
                           user_line_chart_weight=user_line_chart_weight,
                           user_line_chart_cgm=user_line_chart_cgm
                           )

@app.get("/notifications")
@login_required
@access_log
def get_notifications():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()
    return render_template('notifications/notifications.html', user_notifications=user_notifications)

@app.route('/test_neo4j')
@login_required
@access_log
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
@login_required
@access_log
def get_postgreql():
   query = 'SELECT * FROM users limit 1;'
   users = db.session.execute(text(query)).all()
   print(users)
   return str(users)

@app.route('/test_mysql')
@login_required
@access_log
def get_mysql():
   query = 'SELECT * from users u;'
   users = db.session.execute(text(query)).fetchall()
   return str(users)

@app.route('/test_openai')
@login_required
@access_log
def get_openai():
   analyzer = MessangeAnalyzer('English')
   analyzer_response = analyzer.evaluate("2024-05-11T00:38:21.439536 Dinner Salt, Tofu, Spices 2024-05-09T21:29:21.439536 Dinner Herbs, Salt, Lentils 2024-05-09T10:36:21.439536 Lunch Chicken breast, Cereal, Lentils, Soy sauce 2024-05-07T18:37:21.439536 Dinner Beans, Strawberries, Tofu 2024-05-06T20:21:21.439536 Dinner Mayonnaise, Tuna, Oats 2024-05-05T21:26:21.439536 Lunch Raspberries, Herbs, Maple syrup, Beans, Oats 2024-05-05T13:54:21.439536 Dinner Cucumber, Eggs, Carrot 2024-05-11T08:32:21.219779 104 2024-05-10T07:56:21.219779 96 2024-05-08T17:46:21.219779 98 2024-05-08T05:43:21.219779 158 2024-05-07T08:09:21.219779 161 2024-05-06T03:51:21.219779 171 2024-05-05T00:20:21.219779 193")
   return analyzer_response

@app.route('/settings')
@login_required
@access_log
def get_settings():
    # user = current_user
    return render_template("settings/settings.html")

@app.route('/access_logs')
@login_required
@access_log
def get_access_logs():
    access_logs = Access_Log.query.join(Access_Log.user_access).all()
    return render_template("cybersecurity/access_logs.html", access_logs=access_logs)

@app.route('/patients')
@login_required
@access_log
@doctor_admin_only
def get_all_patients():
    patients = Users.query.where(text(f"users.permission='user' and users.active=1")).all()
    return render_template("users/patients.html", patients=patients)

@app.route('/doctors')
@login_required
@access_log
@admin_only
def get_all_doctors():
    doctors = Users.query.filter_by(permission="doctor").join(Users.user_raw).all() 
    return render_template("users/doctors.html", doctors=doctors)

@app.route('/user_settings', methods=['GET','POST'])
@login_required
@access_log
def user_settings():
    if request.method== "GET":
        # updated_user = Users.query.get(current_user.user_id)
        return render_template("users/user_settings.html", user=current_user)
    elif request.method == "POST":
        print("aha")
        updated_user = Users.query.get(current_user.user_id)
        print(updated_user.name)
        updated_user.email = request.form.get('email')
        updated_user.password = request.form.get('password')
        updated_user.name = request.form.get('name')

        db.session.commit()
        flash("Your Settings have been updated successfully!")
        return render_template("users/user_settings.html", user=updated_user)

@app.route('/upload_files', methods=['GET','POST'])
@login_required
@access_log
def route_upload_files():
   if request.method == "GET":
       user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()
       return render_template("data_integration/upload_file.html", user_notifications=user_notifications)
   elif request.method == "POST" and request.files["file"] != "":
            user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()
            try:
                f = request.files["file"]
                # Read the data
                _, ext = os.path.splitext(f.filename)
                if str(ext) == ".csv":
                    df = pd.read_csv(f)
                elif f.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or f.content_type == "application/vnd.ms-excel":
                    df = pd.read_excel(f)
                
                # Connect to KG
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    print("connected to KG-db")
                
                # Select case based on record type
                if f.filename[:1] == "1": # CGM
                    for row in range(len(df[:2])): # TODO: Currently limited for testing purpose
                        glucose_id = uuid1()
                        new_data_glucose = Record_Glucose_Monitoring(gm_entry_id=glucose_id, 
                                                                     timestamp=df.iloc[row]['date and time'],
                                                                       glucose_level=df.iloc[row]['glucose'],
                                                                       device_id=df.iloc[row]['device_id'],
                                                                       user_id=current_user.user_id)
                        db.session.add(new_data_glucose)
                        db.session.commit()
                        sleep(0.01) # Prevent same uuid

                    # Status: Inserting of neo4j records
                    create_glucose_data(driver, current_user.user_id, df[1:10]) # TODO: Currently limited for testing purpose
                    flash(f"{len(df)} blood glucose records are added successfully!")

                    # Reset the file
                    # request.files["file"] = "" <- TODO: this doesnt work
                    return render_template("data_integration/upload_file.html", user_notifications=user_notifications)
                
                else:
                    raise KeyError() # not recognized file
            except Exception as e:
                return f"Error: {e.__context__}"

@app.route('/records_glucose_monitoring')
@login_required
def get_records_glucose_monitoring():
    # get all glucose data for recent 7 days
    records_glucose_monitoring = Record_Glucose_Monitoring.filter_by(user_id=current_user.user_id).all()
    # return all as SQLAlchemy object
    return records_glucose_monitoring


@app.route('/healthcare_providers')
@login_required
@access_log
def get_healthcare_providers():
    healthcare_providers = Users.query.filter_by(permission="doctor").join(Users.user_raw).all() 
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()
    return render_template("home/healthcare_providers.html", healthcare_providers=healthcare_providers,
                           user_notifications=user_notifications)


@app.route('/healthcare_provider/<string:user_id>')
@login_required
@access_log
def get_one_healthcare_provider(user_id):
    print(user_id)
    healthcare_provider = Users.query.filter_by(user_id=str(user_id)).join(Users.user_raw).first() 
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()
    return render_template("home/healthcare_provider.html", healthcare_provider=healthcare_provider,
                           user_notifications=user_notifications)




# 404-error handler    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_handler/page-404.html'), 404

if __name__ == '__main__':
    app.run()