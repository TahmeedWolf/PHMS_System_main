from data_integration.template_download import *
from extension import db
from uuid import uuid1
from time import sleep
import pandas as pd
from sqlalchemy import text
import os
from tqdm import tqdm

# Models.Records
from Models.Records.Records_Glucose_Monitoring import *
from Models.Records.Records_Food_Intake import *
from Models.Records.Records_Insulin_Intake import *
from Models.Records.Records_Physical_Activity import *
from Models.Records.Records_Weight_Tracking import *
from Models.Records.Records_Cholesterol import *
from Models.Records.Records_Hba1C import *
from Models.Records.Records_Blood_Pressure import *

# Templates, Samples, attributes in each record type
from data_integration.template_download import *

"""This file handles all upload files"""
# 
def data_extract(f):
    """Check if the file type is the accepted formats"""
    # Read the data
    try:
        print(f.filename)
        filename, ext = os.path.splitext(f.filename)
        print(filename)
        print(ext)
        if str(ext) == ".csv":
            print("is csv!")
            df = pd.read_csv(f)
        elif f.content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" or f.content_type == "application/vnd.ms-excel":
            print("is excel!")
            df = pd.read_excel(f)
        print("done extraction")
        return df
    except Exception as e:
            return f"Error: {e.__context__}"


def data_insert(key, df, attributes, current_user, driver):
    print("start selecting")
    if key == "records_glucose_monitoring":
        message = data_insert_internal(df=df, record_class=Records_Glucose_Monitoring, attributes=attributes , current_user=current_user, key=key, kg_driver=driver)
    elif key == "records_food_intake":
        message = data_insert_internal(df=df, record_class=Records_Food_Intake, attributes=attributes, current_user=current_user, key=key, kg_driver=driver)
    elif key == "records_insulin_intake":
        message = data_insert_internal(df=df, record_class=Records_Insulin_Intake, attributes=attributes, current_user=current_user, key=key, kg_driver=driver)
    elif key == "records_physical_activity":
        message = data_insert_internal(df=df, record_class=Records_Physical_Activity , attributes=attributes, current_user=current_user, key=key, kg_driver=driver)
    elif key == "records_weight_tracking":
        message = data_insert_internal(df=df, record_class=Records_Weight_Tracking, attributes=attributes, current_user=current_user, key=key, kg_driver=driver)
    elif key == "records_cholesterol":
        message = data_insert_internal(df=df, record_class=Records_Cholesterol, attributes=attributes, current_user=current_user, key=key, kg_driver=driver)
    elif key == "records_hba1c":
        message = data_insert_internal(df=df, record_class=Records_Hba1C, attributes=attributes, current_user=current_user, key=key, kg_driver=driver)
    elif key == "records_blood_pressure":
        message = data_insert_internal(df=df, record_class=Records_Blood_Pressure, attributes=attributes, current_user=current_user, key=key, kg_driver=driver)
    return message

    
def data_insert_internal(df, record_class , attributes:list , current_user, key, kg_driver):
    # start extracting the attributes
    for row in tqdm(range(len(df))):
        entry_id = uuid1()
        new_entry = record_class(entry_id= entry_id, user_id=current_user.user_id)
        for attribute in attributes:
            # add all attributes in
            new_entry[attribute] = df.iloc[row][attribute]
        db.session.add(new_entry)

        # Knowledge Graph Data Insertion
        # Create a User node if it doesn't exist
        kg_driver.execute_query("MERGE (p:Patient {{id: '{0}'}}) RETURN p;".format(current_user.user_id), database_="neo4j")
        kg_class = key.title()

        node_attributes = ""
        for attribute in attributes:
            if attribute == attributes[0]:
                if type(df.iloc[row][attribute]) == str: # is string
                    node_attributes = node_attributes + attribute + ":" + '"' + df.iloc[row][attribute] + '"'
                else: #is number
                    node_attributes = node_attributes +  attribute +  ":" + str(df.iloc[row][attribute])
            else:
                if type(df.iloc[row][attribute]) == str: # is string
                    node_attributes = node_attributes + "," +  attribute +  ":" + '"' + df.iloc[row][attribute] + '"'
                else: #is number
                    node_attributes = node_attributes + "," +  attribute +  ":" + str(df.iloc[row][attribute])

        
        # Batch create Record nodes connected to Record Classes
        kg_driver.execute_query(
            """MATCH (p:Patient) WHERE p.id = '{0}' CREATE (p)<-[:RECORDS_FOR]-(gm:{1} {{{2}}});""".format(current_user.user_id, 
                                                                                                    kg_class,
                                                                                                    node_attributes), 
                                                                                                    database_="neo4j")
        sleep(0.02) # Prevent same uuid
        if row%10 == 0:
            # Add in the records to mysql at one time
            db.session.commit()
    db.session.commit()

    return f"{len(df)} records are added successfully!"
