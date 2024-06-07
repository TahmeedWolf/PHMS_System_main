from extension import db
from sqlalchemy import desc

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


