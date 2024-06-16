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

def data_insert_kg(current_user, driver, df:pd.DataFrame, attributes:list):
    # Create a User node if it doesn't exist
    driver.execute_query("MERGE (p:Patient {{id: '{0}'}}) RETURN p;".format(current_user.user_id), database_="neo4j")

    # Batch create Data_Glucose nodes connected to Data_Glucoses
    for row in range(len(df)):
        driver.execute_query(
            """MATCH (p:Patient) WHERE p.id = '{0}' CREATE (p)<-[:RECORDS_FOR]-(gm:Glucose_Monitoring {{level: {1}, timestamp: '{2}'}});""".format(user_id,glucose_readings.iloc[row]['glucose'],glucose_readings.iloc[row]['date and time']), database_="neo4j"
        )
    return "Success"

    # # start extracting the attributes
    # for row in range(len(df)):
    #     entry_id = uuid1()
    #     new_entry = record_class(entry_id= entry_id, user_id=current_user.user_id)
    #     for attribute in attributes:
    #         # add all attributes in
    #         print(f"attribute: {attribute}")
    #         print(df.iloc[row][attribute])
    #         new_entry[attribute] = df.iloc[row][attribute]
    #     db.session.add(new_entry)
    #     db.session.commit()
    #     sleep(0.02) # Prevent same uuid

    # return f"{len(df)} records are added successfully!"

def get_kg_chart_data(driver, user_id):
        """To get dict for drawing knowledge graph at dashboard"""
        driver.verify_connectivity()
        records, summary, keys = driver.execute_query(
            f"""// Match patient nodes connected to glucose monitoring nodes with glucose levels higher than 16
                MATCH (p:Patient)<-[q:RECORDS_FOR]-(g:Records_Glucose_Monitoring)
                WHERE g.glucose_level > 16 and p.id = '{user_id}'

                // From those glucose monitoring nodes, find other record nodes connected to the same patient within a 3-hour window before the glucose reading
                WITH p, g, q, datetime(g.timestamp) AS glucoseTime
                MATCH (p)<-[r:RECORDS_FOR]-(n:Records_Food_Intake)
                WHERE n.timestamp < g.timestamp 
                AND datetime(n.timestamp) >= glucoseTime - duration('PT3H')
                AND NOT n:Records_Glucose_Monitoring

                RETURN p, g, q, r, n ;""",
                            database_="neo4j",
                        )
        kg_data = { "nodeId": '1', "label": 'Patient', "user_id": f"{user_id}", "glucoseData": [], "foodintakeData" : []}
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
        return kg_data