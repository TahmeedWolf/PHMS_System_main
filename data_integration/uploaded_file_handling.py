from data_integration.template_download import *
from extension import db
from uuid import uuid1
from time import sleep
import pandas as pd
from sqlalchemy import text
import os

# Models.Records
from Models.Records.Records_Glucose_Monitoring import *
from Models.Records.Records_Food_Intake import *
from Models.Records.Records_Insulin_Intake import *
from Models.Records.Records_Physical_Activity import *
from Models.Records.Records_Weight_Tracking import *
from Models.Records.Records_Cholesterol import *
from Models.Records.Records_Hba1c import *
from Models.Records.Records_Blood_Pressure import *

# Templates, Samples, attributes in each record type
from data_integration.template_download import *

"""This file handles all upload files"""
# 
def data_extract(f):
    """Check if the file type is the accepted formats"""
    # Read the data
    try:
        _, ext = os.path.splitext(f.filename)
        if str(ext) == ".csv":
            df = pd.read_csv(f)
        elif f.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or f.content_type == "application/vnd.ms-excel":
            df = pd.read_excel(f)
        return df
    except Exception as e:
            return f"Error: {e.__context__}"


def data_insert(key, df, attributes, current_user):
    if key == "records_glucose_monitoring":
        message = data_insert_internal(df, Record_Glucose_Monitoring, attributes , current_user)
    elif key == "records_food_intake":
        message = data_insert_internal(df, Records_Food_Intake, attributes, current_user)
    elif key == "records_insulin_intake":
        message = data_insert_internal(df, Records_Insulin_Intake, attributes, current_user)
    elif key == "records_physical_activity":
        message = data_insert_internal(df,Records_Physical_Activity , attributes, current_user)
    elif key == "records_weight_tracking":
        message = data_insert_internal(df, Records_Weight_Tracking, attributes, current_user)
    elif key == "records_cholesterol":
        message = data_insert_internal(df, Records_Cholesterol, attributes, current_user)
    elif key == "records_hba1c":
        message = data_insert_internal(df, Records_Hba1c, attributes, current_user)
    elif key == "records_blood_pressure":
        message = data_insert_internal(df, Records_Blood_Pressure, attributes, current_user)
    return message

    
def data_insert_internal(df, record_class, attributes, current_user):
    print("start of data_insert_internal")
    # start extracting the attributes
    for row in range(len(df[:2])): # TODO: Currently limited to 1 rows for testing purpose
        entry_id = uuid1()
        new_entry = record_class(entry_id= entry_id, user_id=current_user.user_id)
        for attribute in attributes:
            # add all attributes in
            print(f"attribute: {attribute}")
            print(df.iloc[row][attribute])
            new_entry[attribute] = df.iloc[row][attribute]
        db.session.add(new_entry)
        db.session.commit()
        sleep(0.02) # Prevent same uuid


    # Status: Inserting of neo4j records
    # create_glucose_data(driver, current_user.user_id, df[1:10]) # TODO: Currently limited for testing purpose
    return f"{len(df)} records are added successfully!"

    # Reset the file
    # request.files["file"] = "" <- TODO: this doesnt work
