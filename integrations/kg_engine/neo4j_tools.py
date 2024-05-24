import pandas as pd

def create_glucose_data(driver, user_id, glucose_readings:pd.DataFrame):
    # Create a User node if it doesn't exist
    driver.execute_query("MERGE (p:Patient {{id: '{0}'}}) RETURN p;".format(user_id), database_="neo4j")

    # Batch create Data_Glucose nodes connected to Data_Glucoses
    for row in range(len(glucose_readings)):
        driver.execute_query(
            """MATCH (p:Patient) WHERE p.id = '{0}' CREATE (p)<-[:RECORDS_FOR]-(gm:Glucose_Monitoring {{level: {1}, timestamp: '{2}'}});""".format(user_id,glucose_readings.iloc[row]['glucose'],glucose_readings.iloc[row]['date and time']), database_="neo4j"
        )
    return "Success"