from flask import Flask, request, render_template, flash, url_for, redirect, Response, jsonify
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from sqlalchemy import text, desc
from uuid import uuid1
from integrations.kg_engine.neo4j_tools import *
from integrations.nlg.MessageAnalyzer import MessangeAnalyzer
from flask_bootstrap import Bootstrap5

# Models
from Models.Users import *
from Models.Notifications import *
from Models.Authentication import *
# Models.Records
from Models.Records.Records_Cholesterol import *
from Models.Records.Records_Food_Intake import *
from Models.Records.Records_Glucose_Monitoring import *
from Models.Records.Records_Hba1C import *
from Models.Records.Records_Insulin_Intake import *
from Models.Records.Records_Physical_Activity import *
from Models.Records.Records_Weight_Tracking import *
from Models.Records.Records_Blood_Pressure import *

# Insights
from integrations.nlg.insight_types import *

# Templates, Samples, attributes in each record type
from data_integration.template_download import *
# Handle all uploaded file
from data_integration.uploaded_file_handling import *
import pandas as pd

# Dashboard
from data_integration.dashboard_data_query import *
# Display time on dashboard
from datetime import datetime, timezone

# Security
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from cybersecurity.authentication import *

# ---------------------------------------------------------------------------- #
#                               Main System Setup                              #
# ---------------------------------------------------------------------------- #

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

# ---------------------------------------------------------------------------- #
#                              Dual-Database Setup                             #
# ---------------------------------------------------------------------------- #

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

# ---------------------------------------------------------------------------- #
#                                  Login Setup                                 #
# ---------------------------------------------------------------------------- #

# Configure Flask-Login's Login Manager
login_manager = LoginManager()
login_manager.init_app(app)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    
    return db.get_or_404(Users, user_id)


# Redirect to login when user is not logged in (with default message)
login_manager.login_view = "login"

# Index route to fix bug
@app.route('/')
@login_required
def index():
    if current_user.permission == "user":
        return redirect(url_for("home"))
    elif current_user.permission == "admin" or current_user.permission == "doctor":
        return redirect(url_for("get_overview"))
    else:
        return redirect(url_for("page_not_found"))

# Chat route 
@app.route('/chat')
def chat():
    return render_template('home/chat.html')

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
            return render_template('home/login.html')
        # Check stored password hash against entered password hashed.
        elif not check_password_hash(user.password, password):
            flash("Password incorrect. Please try again.")
            return render_template('home/login.html')
        elif user.is_active == 0:
            flash("This account is no longer active.")
            return render_template('home/login.html')
        else:
            login_user(user)
            return redirect(url_for('index'))
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
        if user and int(user.active) ==1:
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
        user_weight = Records_Weight_Tracking(entry_id=user_weight_uuid, weight=weight,user_id=current_user.user_id)
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
        if user and int(user.active) ==1:
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

# ---------------------------------------------------------------------------- #
#                                   Homepage                                   #
# ---------------------------------------------------------------------------- #

@app.get("/")
@login_required
def landing():
    return redirect(url_for("home"))

@app.get("/home")
@login_required
@access_log
def home():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    if request.args.get('user_id') is None:
        user_id = current_user.user_id
    elif current_user.permission == 'admin' or current_user.permission == 'doctor' and request.args.get('user_id') is not None:
        user_id = request.args.get('user_id')
        patient_notification_one = Notifications.query.where(text(f"notification_logs.to_user_id='{user_id}'")).order_by(desc(Notifications.created_time)).first()
    else:
        user_id = current_user.user_id
    user = Users.query.filter_by(user_id=user_id).first()

    if user.birthday:
        year = user.birthday.strftime("%Y")
        current_year = datetime.now().strftime("%Y")
        age = int(current_year) - int(year)
    else:
        age=0

    # ------------------------ Retrieve data for dashboard ----------------------- #
    records_glucose_monitoring = get_dashboard_data(Records_Glucose_Monitoring, user_id=user.user_id)
    records_hba1c = get_dashboard_data(Records_Hba1C, user_id=user.user_id)
    records_weight_tracking = get_dashboard_data(Records_Weight_Tracking, user_id=user.user_id)
    records_cholesterol = get_dashboard_data(Records_Cholesterol, user_id=user.user_id)
    records_blood_pressure = get_dashboard_data_bp(user_id=user.user_id)
    records_food_intake = Records_Food_Intake.query.filter_by(user_id=user_id).order_by(desc(Records_Food_Intake.timestamp)).limit(10).all()

    # --------------------------- Retrieve data for kg --------------------------- #
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        kg_data = get_kg_chart_data(driver=driver, user_id=user.user_id)

    if 'patient_notification_one'not in locals() and len(user_notifications) != 0:
        patient_notification_one = user_notifications[0]
    else:
        patient_notification_one = ""

    # Set-up current datetime in template
    current_datetime = datetime.now(timezone.utc)

    # Check if 'age' is defined to decide which template variables to pass
    if age is not None:
        return render_template('home/index.html', user=user,
                               age=age,
                               records_glucose_monitoring=records_glucose_monitoring,
                               patient_notification_one=patient_notification_one,
                               records_hba1c=records_hba1c,
                               records_weight_tracking=records_weight_tracking,
                               records_blood_pressure=records_blood_pressure,
                               records_cholesterol=records_cholesterol,
                               user_notifications=user_notifications,
                               records_food_intake=records_food_intake,
                               kg_data=kg_data,
                               current_datetime=current_datetime
                               )
    else:
        return render_template('home/index.html', user=user,
                               records_glucose_monitoring=records_glucose_monitoring,
                               records_hba1c=records_hba1c,
                               records_weight_tracking=records_weight_tracking,
                               records_blood_pressure=records_blood_pressure,
                               records_cholesterol=records_cholesterol,
                               user_notifications=user_notifications,
                               records_food_intake=records_food_intake,
                               current_datetime=current_datetime
                               )


# ---------------------------------------------------------------------------- #
#                             Overview Page                                    #
# ---------------------------------------------------------------------------- #

# ----------------------------- Doctor's Overview ---------------------------- #
@app.route('/overview')
@login_required
@access_log
@doctor_admin_only
def get_overview():
    """This endpoints delivers a top-overview of all registered patients."""
    user_count = Users.query.where(text(f"users.permission='user'")).count()
    active_user_count = Users.query.where(text(f"users.permission='user' and users.active=1")).count()
    doctor_user_count = Users.query.where(text(f"users.permission='doctor' and users.active=1")).count()
    avg_glucose_levels = db.session.execute(text("select round(avg(rgm.glucose_level),2) from records_glucose_monitoring rgm;")).first()
    # print(avg_glucose_levels[0])

    # -- Record of patient who has higher or lower than critical glucose levels (Lower) -- #
    patient_record_low = Records_Glucose_Monitoring.query.where(text("glucose_level < 4")).join(Records_Glucose_Monitoring.data_cgm).order_by(desc(Records_Glucose_Monitoring.timestamp)).limit(10).all()
    # -- Record of patient who has higher or lower than critical glucose levels (Higher) -- #
    patient_record_high = Records_Glucose_Monitoring.query.where(text("glucose_level > 10")).join(Records_Glucose_Monitoring.data_cgm).order_by(desc(Records_Glucose_Monitoring.timestamp)).limit(10).all()

    # ------------------- Histogram of patient's Glucose levels ------------------ #
    data_glucose_hist = get_overview_glucose_data()

    # ------------------------ Histogram of patient's BMI ------------------------ #
    data_bmi_hist = get_overview_bmi_data()

    # -------------------- Histogram of patient's hba1c levels ------------------- #
    data_hba1c_hist = get_overview_hba1c_data()

    # Set-up current datetime in template
    current_datetime = datetime.now(timezone.utc)
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()

    # dict = [user_count, active_user_count, avg_glucose_levels[0], patient_record_low, patient_record_high]
    return render_template("home/overview.html", 
                           user_count=user_count, 
                           current_datetime=current_datetime,
                           active_user_count=active_user_count,
                           doctor_user_count=doctor_user_count,
                           avg_glucose_levels=avg_glucose_levels[0],
                           patient_record_low=patient_record_low,
                           patient_record_high=patient_record_high,
                           data_glucose_hist=data_glucose_hist, 
                           data_bmi_hist=data_bmi_hist,
                           data_hba1c_hist=data_hba1c_hist,
                           user_notifications=user_notifications)

# ---------------------------------------------------------------------------- #
#                           Upload of Healthcare Data                          #
# ---------------------------------------------------------------------------- #

@app.get("/data/template_download")
@login_required
@access_log
def get_template_download():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    return render_template('data_integration/template_download.html', user_notifications=user_notifications, download=download)

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
                # Connect to KG
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    driver.verify_connectivity()
                    print("connected to KG-db")
                
                filename, _ = os.path.splitext(f.filename)
                filename = filename.lower()
                filename = filename.replace("_sample", "")
                filename = filename.replace("_template", "")

                key = "records_" + filename[2:]
                # Sanitize the name
                key = key.replace(" ", "")
                key = key.replace("(", "")
                key = key.replace(")", "")
                while key[-1].isdigit():
                    key = key[:-1]
                # Remove all numbers in filename

                print("before extract")
                print(key)
                if key in records_list.keys():
                    attributes = records_list[key]
                    print(attributes)
                    df = data_extract(f)
                else:
                    flash("Error: Incorrect file uploaded. Please try again.")
                    return render_template("data_integration/upload_file.html", user_notifications=user_notifications)
                print("before data_insert")
                # inserting of record including selection of different class depend on key, insert into kg and db
                # df = df[:25] # Uncomment this for testing purpose
                print(df.info())
                message = data_insert(key=key, df=df,attributes=attributes, current_user=current_user, driver=driver)
                print("after data insertion")
                flash(message)
                
                # else:
                #     raise KeyError() # not recognized file
                # return render_template(f"data_integration/get_{key}.html", user_notifications=user_notifications)
                return redirect(url_for(f'get_{key}'))
            except Exception as e:
                return f"Error: {e.__context__}"
            
# ---------------------------------------------------------------------------- #
#                        Retrieve All User Uploaded Data                       #
# ---------------------------------------------------------------------------- #

@app.get("/data/records_glucose_monitoring")
@login_required
@access_log
def get_records_glucose_monitoring():
    records = Records_Glucose_Monitoring.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Glucose_Monitoring.timestamp)).all()
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    return render_template('data_integration/get_records_glucose_monitoring.html',
                           records=records,
                            user_notifications=user_notifications)

@app.get("/data/records_food_intake")
@login_required
@access_log
def get_records_food_intake():
    records = Records_Food_Intake.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Food_Intake.timestamp)).all()
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    return render_template('data_integration/get_records_food_intake.html',
                           records=records,
                           user_notifications=user_notifications)

@app.get("/data/records_insulin_intake")
@login_required
@access_log
def get_records_insulin_intake():
    records = Records_Insulin_Intake.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Insulin_Intake.timestamp)).all()
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    return render_template('data_integration/get_records_insulin_intake.html',
                           records=records,
                           user_notifications=user_notifications)

@app.get("/data/records_physical_activity")
@login_required
@access_log
def get_records_physical_activity():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    records = Records_Physical_Activity.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Physical_Activity.timestamp)).all()
    return render_template('data_integration/get_records_physical_activity.html',
                           records=records,
                           user_notifications=user_notifications)

@app.get("/data/records_weight_tracking")
@login_required
@access_log
def get_records_weight_tracking():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    records = Records_Weight_Tracking.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Weight_Tracking.timestamp)).all()
    return render_template('data_integration/get_records_weight_tracking.html',
                           records=records,
                           user_notifications=user_notifications)

@app.get("/data/records_cholesterol")
@login_required
@access_log
def get_records_cholesterol():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    records = Records_Cholesterol.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Cholesterol.timestamp)).all()
    return render_template('data_integration/get_records_cholesterol.html',
                           records=records,
                           user_notifications=user_notifications)

@app.get("/data/records_hba1c")
@login_required
@access_log
def get_records_hba1c():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    records = Records_Hba1C.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Hba1C.timestamp)).all()
    return render_template('data_integration/get_records_hba1c.html',
                           records=records,
                           user_notifications=user_notifications)

@app.get("/data/records_blood_pressure")
@login_required
@access_log
def get_records_blood_pressure():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    records = Records_Blood_Pressure.query.filter_by(user_id=current_user.user_id).order_by(desc(Records_Blood_Pressure.timestamp)).all()
    return render_template('data_integration/get_records_blood_pressure.html',
                           records=records,
                           user_notifications=user_notifications)

# ---------------------------------------------------------------------------- #
#                                 Notifications                                #
# ---------------------------------------------------------------------------- #

@app.get("/notifications")
@login_required
@access_log
def get_notifications():
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    if len(user_notifications) == 0:
        error = "Error:no_record"
    else:
        error = ""
    return render_template('notifications/notifications.html',
                           user_notifications=user_notifications,
                           insight_list=insight_list,
                           error=error)

@app.route("/insight_generation")
@login_required
def route_generate_insights():
    insight_type = request.args.get('insight_type')
    analyzer = MessangeAnalyzer('English')
    data_classes = insight_list[insight_type]["data"]
    
    data = ""
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        for data_class in data_classes:
            if data_class.__name__ == "Records_Glucose_Monitoring":
                # Shorten the query if data is cgm
                records, summary, keys = driver.execute_query(
                    f"""MATCH (p:Patient WHERE p.id='{current_user.user_id}')<- [r:RECORDS_FOR]-(gm:{data_class.__name__}) RETURN gm.timestamp, gm.glucose_level limit 20;""",
                    database_="neo4j",
                )
            else:
                records, summary, keys = driver.execute_query(
                    f"""MATCH (p:Patient WHERE p.id='{current_user.user_id}')<- [r:RECORDS_FOR]-(n:{data_class.__name__}) WHERE NOT n:Records_Glucose_Monitoring RETURN n limit 20;""",
                    database_="neo4j",
                )

            if records:
                data =  data + str(records) # records.data()
            else:
                flash(f"Error: Data Insufficient {data_class.__name__}.")
                return redirect(url_for('get_notifications'))
    # print(data)

    prompt = insight_list[insight_type]["prompt"]
    # print(prompt)

    analyzer_response = analyzer.evaluate(data=data, prompt=prompt)
    # ------------------------------ sanitize reply ------------------------------ #
    analyzer_response = analyzer_response.replace("*","")

    new_notification = Notifications(notification_content=analyzer_response,
                                    to_user_id=current_user.user_id,
                                        type=insight_type)

    db.session.add(new_notification)
    db.session.commit()
    print("An new insight has been added.")
    flash("An new insight has been added.")
    return redirect(url_for('get_notifications'))

# ---------------------------------------------------------------------------- #
#                                 Testing Tools                                #
# ---------------------------------------------------------------------------- #

@app.route('/test_neo4j')
@login_required
@admin_only
@access_log
def get_neo4j():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        records, summary, keys = driver.execute_query(
            f"""// Match patient nodes connected to glucose monitoring nodes with glucose levels higher than 16
                MATCH (p:Patient)<-[q:RECORDS_FOR]-(g:Records_Glucose_Monitoring)
                WHERE g.glucose_level > 16 and p.id = 'fa15ab8c-16bc-11ef-93c9-28d0ea7c5d57'

                // From those glucose monitoring nodes, find other record nodes connected to the same patient within a 3-hour window before the glucose reading
                WITH p, g, q, datetime(g.timestamp) AS glucoseTime
                MATCH (p)<-[r:RECORDS_FOR]-(n:Records_Food_Intake)
                WHERE n.timestamp < g.timestamp 
                AND datetime(n.timestamp) >= glucoseTime - duration('PT3H')
                AND NOT n:Records_Glucose_Monitoring

                RETURN p, g, q, r, n ;""",
                            database_="neo4j",
                        )
        kg_data = { "nodeId": '1', "label": 'Patient', "user_id": f"{current_user.user_id}", "glucoseData": [], "foodintakeData" : []}
        for record in records:
            glucose_level = record.data()["g"]["glucose_level"]
            timestamp = record.data()["g"]["timestamp"]
            raw_glucose = {"glucose_level": str(glucose_level), "timestamp": str(timestamp)}
            if raw_glucose not in kg_data["glucoseData"]:
                # print(f"raw: {raw_glucose}")
                kg_data["glucoseData"].append(raw_glucose)

            food_items = record.data()["n"]["food_items"]
            timestamp = record.data()["n"]["timestamp"]
            raw_food_items = {"food_items": str(food_items), "timestamp": str(timestamp), "value": str(record.data()["n"]["carbohydrates"])}
            if raw_food_items not in kg_data["foodintakeData"]:
                # print(f"food items checking: {food_items}")
                kg_data["foodintakeData"].append(raw_food_items)
        print(kg_data)
        return render_template("test_visjs.html", kg_data=kg_data)



@app.route('/test_openai')
@login_required
@admin_only
@access_log
def get_openai():
   analyzer = MessangeAnalyzer('English')
   analyzer_response = analyzer.evaluate("2024-05-11T00:38:21.439536 Dinner Salt, Tofu, Spices 2024-05-09T21:29:21.439536 Dinner Herbs, Salt, Lentils 2024-05-09T10:36:21.439536 Lunch Chicken breast, Cereal, Lentils, Soy sauce 2024-05-07T18:37:21.439536 Dinner Beans, Strawberries, Tofu 2024-05-06T20:21:21.439536 Dinner Mayonnaise, Tuna, Oats 2024-05-05T21:26:21.439536 Lunch Raspberries, Herbs, Maple syrup, Beans, Oats 2024-05-05T13:54:21.439536 Dinner Cucumber, Eggs, Carrot 2024-05-11T08:32:21.219779 104 2024-05-10T07:56:21.219779 96 2024-05-08T17:46:21.219779 98 2024-05-08T05:43:21.219779 158 2024-05-07T08:09:21.219779 161 2024-05-06T03:51:21.219779 171 2024-05-05T00:20:21.219779 193")
   return analyzer_response

# ---------------------------------------------------------------------------- #
#                             Patients and Patient                             #
# ---------------------------------------------------------------------------- #
@app.route('/patients')
@login_required
@access_log
@doctor_admin_only
def get_all_patients():
    patients = Users.query.where(text(f"users.permission='user' and users.active=1")).all()
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    return render_template("users/patients.html", 
                           patients=patients, 
                           user_notifications=user_notifications)


# ---------------------------------------------------------------------------- #
#                              Doctors and Doctor                              #
# ---------------------------------------------------------------------------- #

@app.route('/doctors')
@login_required
@access_log
@admin_only
def get_all_doctors():
    doctors = Users.query.filter_by(permission="doctor").outerjoin(Users.user_raw).all()
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
    return render_template("users/doctors.html", 
                           doctors=doctors,
                           user_notifications=user_notifications)

# @app.route('/doctors/<string:user_id>')
# @login_required
# @access_log
# @admin_only
# def get_one_doctor(user_id):
#     """Update other user's setting (Admin-only)"""
#     doctor = Users.query.filter_by(user_id=user_id).all()
#     user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).limit(5).all()
#     return render_template("users/user_settings.html", 
#                            user=doctor,
#                            user_notifications=user_notifications)

# ---------------------------------------------------------------------------- #
#                                 User Settings                                #
# ---------------------------------------------------------------------------- #

# @app.route('/settings')
# @login_required
# @access_log
# def get_settings():
#     # user = current_user
#     return render_template("settings/settings.html")


@app.route('/user_settings', methods=['GET','POST'])
@login_required
@access_log
def user_settings():
    if request.method== "GET":
        user_id = request.args.get('user_id')
        if user_id == current_user.user_id or user_id is None or len(user_id) == 0:
            return render_template("users/user_settings.html", user=current_user)
        elif user_id != current_user.user_id and current_user.permission == 'admin':
            user = Users.query.get(user_id)
            return render_template("users/user_settings.html", user=user)
    elif request.method == "POST":
        if request.args.get('user_id') == current_user.user_id:
            updated_user = Users.query.get(current_user.user_id)
            updated_user.email = request.form.get('email')
            updated_user.password = request.form.get('password')
            updated_user.name = request.form.get('name')
            updated_user.gender = request.form.get('gender')
            db.session.commit()
            flash("Settings have been updated successfully!")
            return render_template("users/user_settings.html", user=updated_user)
        elif current_user.permission == 'admin':
            user_id = request.args.get('user_id')
            updated_user = Users.query.get(user_id)
            updated_user.email = request.form.get('email')
            updated_user.password = request.form.get('password')
            updated_user.name = request.form.get('name')
            updated_user.gender = request.form.get('gender')
            db.session.commit()
            flash("Settings have been updated successfully!")
            return render_template("users/user_settings.html", user=updated_user)
        else:
            flash("Error")
            return render_template("users/user_settings.html", user=current_user)

# ---------------------------------------------------------------------------- #
#                                  Admin Tools                                 #
# ---------------------------------------------------------------------------- #
# ---------------------------- Healthcare Provider --------------------------- #

@app.route('/healthcare_providers')
@login_required
# @admin_only
@access_log
def get_healthcare_providers():
    healthcare_providers = Users.query.filter_by(permission="doctor").outerjoin(Users.user_raw).all() 
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()
    return render_template("home/healthcare_providers.html", healthcare_providers=healthcare_providers,
                           user_notifications=user_notifications)

@app.route('/healthcare_provider/<string:user_id>')
@login_required
# @admin_only
@access_log
def get_one_healthcare_provider(user_id):
    healthcare_provider = Users.query.filter_by(user_id=str(user_id)).join(Users.user_raw).first() 
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).all()
    return render_template("home/healthcare_provider.html", healthcare_provider=healthcare_provider,
                           user_notifications=user_notifications)

@app.route('/access_logs')
@login_required
@admin_only
@access_log
def get_access_logs():
    access_logs = Access_Log.query.all()
    return render_template("cybersecurity/access_logs.html", access_logs=access_logs)


# ---------------------------------------------------------------------------- #
#                                 Miscellaneous                                #
# ---------------------------------------------------------------------------- #

@app.route("/contact_us", methods=["GET", "POST"])
@login_required
@access_log
def route_contact_us():
    # TODO: finish this
    user_notifications = Notifications.query.filter_by(to_user_id=current_user.user_id).order_by(desc(Notifications.created_time)).all()
    return render_template('forms/contact_us.html', user_notifications=user_notifications)

@app.route("/terms_and_condition", methods=["GET"])
def get_tnc():
    return render_template('forms/terms_and_condition.html')

# 404-error handler    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error_handler/page-404.html'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0')