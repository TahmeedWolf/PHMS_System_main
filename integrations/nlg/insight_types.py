# -------------------------- Import all Record Class ------------------------- #
from Models.Records.Records_Glucose_Monitoring import *
from Models.Records.Records_Food_Intake import *
from Models.Records.Records_Insulin_Intake import *
from Models.Records.Records_Physical_Activity import *
from Models.Records.Records_Weight_Tracking import *
from Models.Records.Records_Cholesterol import *
from Models.Records.Records_Hba1C import *
from Models.Records.Records_Blood_Pressure import *

# ---------------------------------------------------------------------------- #
#                        Types of NLG that PHMS provides                       #
# ---------------------------------------------------------------------------- #

insight_list = {
    "dietary" : {"data":[Records_Glucose_Monitoring, Records_Food_Intake],
                 "prompt": "Analyze my meal logs and recent CGM data to identify any correlations between food intake and glucose spikes. Provide dietary recommendations that could help stabilize glucose levels."},
    "physical_activity" : {"data" : [Records_Glucose_Monitoring, Records_Physical_Activity],
                           "prompt": "Review my physical activity data and recent CGM data. Suggest physical activities that could help improve their glucose management based on observed trends and past activity levels."},
    "weight_management" : {"data": [Records_Glucose_Monitoring, Records_Weight_Tracking, Records_Food_Intake],
                           "prompt": "Analyze my weight tracking data alongside their meal logs and exercise data. Offer guidance on how they might manage their weight more effectively to impact their blood glucose control positively."},
    "blood_pressure" : {"data":[Records_Blood_Pressure, Records_Food_Intake],
                        "prompt": "Evaluate my blood pressure and cholesterol levels over the past months. Suggest lifestyle modifications or alert the need for potential medical review to manage cardiovascular health risks."},
    "comprehensive_health_review" : {"data": [Records_Glucose_Monitoring, Records_Blood_Pressure, Records_Hba1C, Records_Weight_Tracking, Records_Cholesterol, Records_Physical_Activity],
                                     "prompt": "Compile all my recent health data including CGM, blood pressure, HbA1c, weight, exercises and cholesterol. Based on trends and current levels, suggest personalized health goals for the next review period and strategies to achieve these goals."},
    "glucose_trends" : {"data": [Records_Glucose_Monitoring],
                        "prompt": "Analyze my recent blood glucose level. Identify any glucose spikes or low glucose. Provide information of glucose spikes, low glucose, trends of glucose levels and average of glucose level."},
    "physical_activity_trends" : {"data": [Records_Physical_Activity],
                        "prompt": """Given the following physical activity records detailing the type of activity, duration, and intensity, analyze the trends over the past month to identify patterns in activity levels and intensity. Assess whether the current level of physical activity aligns with recommended guidelines for maintaining or improving overall health, particularly focusing on cardiovascular health and weight management. Provide personalized recommendations to optimize the physical activity regimen based on observed trends and any identified gaps. Consider suggesting adjustments in activity type, duration, or intensity to enhance health outcomes.Generate a summary that includes:
                                    1. A comparison of weekly physical activity levels and intensities over the month.
                                    2. Analysis of the diversity of activities and their potential benefits for different health aspects.
                                    3. Recommendations for modifying the activity types, durations, or intensities to better align with health goals such as improving cardiovascular health, enhancing muscular strength, or aiding in weight loss.
                                    Please provide this analysis in a clear, concise, and actionable manner, highlighting key insights and actionable steps."""},

}
