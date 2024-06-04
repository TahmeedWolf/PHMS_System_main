# Template must be at first one
download =  {
    "Glucose_Monitoring" : {
            "template": "https://phms-80029.s3.amazonaws.com/data/data_template/1_Glucose_Monitoring_Template.xlsx",
            "sample": "https://phms-80029.s3.amazonaws.com/data/data_sample/1_Glucose_Monitoring_Sample.xlsx",
    },
    "Cholesterol" : {
            "template" : "https://phms-80029.s3.amazonaws.com/data/data_template/3_Cholesterol_Template.xlsx",
            "sample" : "https://phms-80029.s3.amazonaws.com/data/data_sample/3_Cholesterol_Sample.xlsx",
    },
    "Blood_Pressure" : {
            "template" : "https://phms-80029.s3.amazonaws.com/data/data_template/2_Blood_Pressure_Template.xlsx",
            "sample" : "https://phms-80029.s3.amazonaws.com/data/data_sample/2_Blood_Pressure_Sample.xlsx",
    },
    "Food_Intake" : {
            "template" : "https://phms-80029.s3.amazonaws.com/data/data_template/4_Food_Intake_Template.xlsx",
            "sample" : "https://phms-80029.s3.amazonaws.com/data/data_sample/4_Food_Intake_Sample.xlsx",
    },
    "HbA1c" : {
            "template" : "https://phms-80029.s3.amazonaws.com/data/data_template/5_HbA1c_Template.xlsx",
            "sample" : "https://phms-80029.s3.amazonaws.com/data/data_sample/5_HbA1c_Sample.xlsx",
    },
    "Insulin_Intake" :{
            "template" : "https://phms-80029.s3.amazonaws.com/data/data_template/6_Insulin_Intake_Template.xlsx",
            "sample" : "https://phms-80029.s3.amazonaws.com/data/data_sample/6_Insulin_Intake_Sample.xlsx",
    },
    "Physical_Activity" :{
            "template" : "https://phms-80029.s3.amazonaws.com/data/data_template/7_Physical_Activity_Template.xlsx",
            "sample" : "https://phms-80029.s3.amazonaws.com/data/data_sample/7_Physical_Activity_Sample.xlsx",

    },
    "Weight_Tracking" : {
            "Weight_Tracking_Template" : "https://phms-80029.s3.amazonaws.com/data/data_template/8_Weight_Tracking_Template.xlsx",
            "sample" : "https://phms-80029.s3.amazonaws.com/data/data_sample/8_Weight_Tracking_Sample.xlsx"
    }
}


records_list = {"records_glucose_monitoring": ["timestamp", "glucose_level", "device_id"], 
                "records_food_intake": ["timestamp", "meal_type", "food_items", "calories", "carbohydrates"], 
                "records_insulin_intake":  ["timestamp", "insulin_type", "dose"],
                "records_physical_activity": ["timestamp", "activity_type", "duration_minute", "intensity"],
                "records_weight_tracking": ["timestamp", "weight"],
                "records_cholesterol" : ["timestamp", "total_cholesterol", "ldl", "hdl", "triglycerides"], 
                "records_hba1c" : ["timestamp", "hba1c"],
                "records_blood_pressure" : ["timestamp", "systolic", "diastolic"]
                }
