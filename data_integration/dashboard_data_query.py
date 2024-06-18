from extension import db
from sqlalchemy import desc, text
import pandas as pd

from Models.Records.Records_Blood_Pressure import *

def get_dashboard_data(record_class, user_id:str) -> dict:
    # Query
    records = record_class.query.filter_by(user_id=user_id).order_by(desc(record_class.timestamp)).limit(25).all()
    
    # if no record returned:
        # exit early
    # else

    value = []
    timestamp = []
    for record in records:
        value.append(record.get_value())
        timestamp.append(str(record.timestamp.strftime("%m-%d %H:%M")))
    data_dict = {"timestamp": timestamp, "value" : value}
    return data_dict

def get_dashboard_data_bp(user_id:str):
    records = Records_Blood_Pressure.query.filter_by(user_id=user_id).order_by(desc(Records_Blood_Pressure.timestamp)).limit(25).all()
    value_systolic = []
    value_diastolic = []
    timestamp = []

    for record in records:
        value_systolic.append(record.get_systolic())
        value_diastolic.append(record.get_diastolic())
        timestamp.append(str(record.timestamp.strftime("%m-%d %H:%M")))
    data_dict = {"timestamp": timestamp, "value_systolic" : value_systolic, "value_diastolic" : value_diastolic}
    return data_dict

def get_overview_glucose_data():
    data_glucose = db.session.execute(text("select * from records_glucose_monitoring;")).all()
    data_glucose = pd.DataFrame(data_glucose)
    # print(data_glucose.head(10))
    bins = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 30]
    data_glucose['binned'] = pd.cut(data_glucose['glucose_level'], bins)
    data_glucose_raw = pd.cut(data_glucose['glucose_level'], bins=bins).value_counts().sort_index()
    # print(data_glucose_raw)
    data_glucose_data = data_glucose_raw.to_list()
    data_glucose_label = bins = ["0-2", "2-4", "4-6", "6-8", "8-10","10-12", "12-14", "14-16", "16-18", "18-20", "20-22", "22-24", "24-26", "26-28"]
    data_glucose_hist = {"label":data_glucose_label, "data": data_glucose_data }

    return data_glucose_hist

def get_overview_bmi_data():
    query = """SELECT
        user_id,
        tbl.weight / (tbl.height * tbl.height) AS bmi
    FROM
        (
        SELECT
            u.user_id,
            max(rwt.weight) AS weight,
            u.height / 100 AS height
        FROM
            records_weight_tracking rwt
        LEFT JOIN users u ON
            u.user_id = rwt.user_id
        GROUP BY
            1) AS tbl;"""
    
    data_raw = db.session.execute(text(query)).all()
    data_raw = pd.DataFrame(data_raw)
    print(data_raw.head(10))
    bins = [0, 18.5, 25.0, 30.0, 40.0]
    data_raw['binned'] = pd.cut(data_raw['bmi'], bins)
    data_raw = pd.cut(data_raw['bmi'], bins=bins).value_counts().sort_index()
    # print(data_glucose_raw)
    data_data = data_raw.to_list()
    data_label = bins = ["0-18.5", "18.5-25.0", "25.0-30.0", "30.0 and above"]
    data_bmi_hist = {"data":data_data, "label": data_label }
    return data_bmi_hist

def get_overview_hba1c_data():
    data_hba1c = db.session.execute(text("select * from records_hba1c;")).all()
    data_hba1c = pd.DataFrame(data_hba1c)
    # print(data_hba1c.head(10))
    bins = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 30]
    data_hba1c['binned'] = pd.cut(data_hba1c['hba1c'], bins)
    data_hba1c_raw = pd.cut(data_hba1c['hba1c'], bins=bins).value_counts().sort_index()
    # print(data_hba1c_raw)
    data_hba1c_data = data_hba1c_raw.to_list()
    data_hba1c_label = bins = ["0-2", "2-4", "4-6", "6-8", "8-10","10-12", "12-14", "14-16", "16-18", "18-20", "20-22", "22-24", "24-26", "26-28"]
    data_hba1c_hist = {"label":data_hba1c_label, "data": data_hba1c_data }
    return data_hba1c_hist