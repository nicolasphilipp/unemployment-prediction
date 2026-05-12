import os
import requests
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("DBREPO_USERNAME")
password = os.getenv("DBREPO_PASSWORD")

# https://test.dbrepo.tuwien.ac.at/database/412fb0ce-5299-4d0e-a271-4641b1365b8a/info
endpoint = "https://test.dbrepo.tuwien.ac.at"
db_id = "412fb0ce-5299-4d0e-a271-4641b1365b8a"

print(f"Targeting database with ID: {db_id}")


# -------- DOES NOT WORK BECAUSE OF INTERNAL SERVER ERROR ---------
# from dbrepo.RestClient import RestClient
# init client for cleanup
# client = RestClient(
#     endpoint=endpoint,
#     username=username,
#     password=password
# )
# cleanup
# print("Checking for existing tables to replace...")
# existing_tables = client.get_tables(database_id=db_id)
# table_map = {table.name: table.id for table in existing_tables}
# tables_to_replace = ["tourism", "unemployment", "measurement_info", "district"]
#
# for table_name in tables_to_replace:
#     if table_name in table_map:
#         print(f"Deleting existing table '{table_name}'...")
#         client.delete_table(database_id=db_id, table_id=table_map[table_name])
#
# print("Cleanup complete. Ready to create new tables.")

# Helper function to create table via direct API
def create_table_via_api(table_payload):
    url = f"{endpoint}/api/v1/database/{db_id}/table"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    res = requests.post(
        url,
        headers=headers,
        auth=(username, password),
        json=table_payload
    )

    if not res.ok:
        print(f"Error creating '{table_payload['name']}': {res.status_code} - {res.text}")
        raise Exception(f"Table '{table_payload['name']}' creation failed.")
    print(f"Successfully created table '{table_payload['name']}' via REST API.")

# create tables
district_payload = {
    "name": "district",
    "description": "Vienna district codes and NUTS identifiers.",
    "is_public": True,
    "is_schema_public": True,
    "columns": [
        {"name": "district_id", "type": "int", "null_allowed": False},
        {"name": "nuts_code", "type": "varchar", "size": 5, "null_allowed": False},
        {"name": "district_code", "type": "int", "null_allowed": False}
    ],
    "constraints": {
        "primary_key": ["district_id"],
        "uniques": [["district_code"]],
        "foreign_keys": []
    }
}
create_table_via_api(district_payload)

measurement_info_payload = {
    "name": "measurement_info",
    "is_public": True,
    "is_schema_public": True,
    "columns": [
        {"name": "district_id", "type": "int", "null_allowed": False},
        {"name": "reference_date", "type": "date", "null_allowed": False},
        {"name": "measurement_id", "type": "int", "null_allowed": False}
    ],
    "constraints": {
        "primary_key": ["district_id", "reference_date"],
        "uniques": [["measurement_id"]],
        "foreign_keys": [
            {
                "columns": ["district_id"],
                "referenced_table": "district",
                "referenced_columns": ["district_id"]
            }
        ]
    }
}
create_table_via_api(measurement_info_payload)

unemployment_payload = {
    "name": "unemployment",
    "is_public": True,
    "is_schema_public": True,
    "columns": [
        {"name": "measurement_id", "type": "int", "null_allowed": False},
        {"name": "gender", "type": "enum", "enums": ["Male", "Female", "Both"], "null_allowed": False},
        {"name": "value", "type": "int", "null_allowed": False},
        {"name": "density", "type": "decimal", "size": 10, "d": 4, "null_allowed": False}
    ],
    "constraints": {
        "foreign_keys": [
            {
                "columns": ["measurement_id"],
                "referenced_table": "measurement_info",
                "referenced_columns": ["measurement_id"]
            }
        ],
        "uniques": [],
        "primary_key": ["measurement_id", "gender"]
    }
}
create_table_via_api(unemployment_payload)

tourism_payload = {
    "name": "tourism",
    "is_public": True,
    "is_schema_public": True,
    "columns": [
        {"name": "measurement_id", "type": "int", "null_allowed": False},
        {"name": "value", "type": "int", "null_allowed": False},
        {"name": "density", "type": "decimal", "size": 10, "d": 4, "null_allowed": False}
    ],
    "constraints": {
        "foreign_keys": [
            {
                "columns": ["measurement_id"],
                "referenced_table": "measurement_info",
                "referenced_columns": ["measurement_id"]
            }
        ],
        "uniques": [],
        "primary_key": ["measurement_id"]
    }
}
create_table_via_api(tourism_payload)


# create the PID for citation
detailed_description = (
    "This database integrates two distinct open government datasets to predict unemployment levels "
    "in Vienna districts using tourism and demographic data. \n\n"

    "Source 1: Unemployed Persons Since 2002 - Districts of Vienna. "
    "Original Publisher: Stadt Wien - Wirtschaft und Finanzen (Open Government Data Austria). "
    "Dataset ID: 9462d680-ede9-40b9-8102-b9baebaa4fbb. "
    "URI: https://www.data.gv.at/katalog/dataset/9462d680-ede9-40b9-8102-b9baebaa4fbb \n\n"

    "Source 2: Guest Overnight Stays Since 2002 - Districts of Vienna. "
    "Original Publisher: Stadt Wien - Wirtschaft und Finanzen (Open Government Data Austria). "
    "Dataset ID: ae4ebf87-9f46-4f05-9e3d-dbff002b216d. "
    "URI: https://www.data.gv.at/katalog/datasets/ae4ebf87-9f46-4f05-9e3d-dbff002b216d"
)

identifier_payload = {
    "type": "database",
    "database_id": db_id,
    "publication_year": 2026,
    "publisher": "Stadt Wien - Wirtschaft und Finanzen",
    "language": "en",
    "titles": [
        {
            "title": "Prediction of unemployment in Vienna districts using tourism and demographic data",
            "language": "en"
        }
    ],
    "descriptions": [
        {
            "description": detailed_description,
            "language": "en",
            "type": "Abstract"
        }
    ],
    "funders": [],
    "licenses": [
        {
            "identifier": "CC-BY-4.0",
            "uri": "https://www.data.gv.at/info/netiquette?locale=de",
            "description": "Creative Commons Attribution 4.0 International"
        }
    ],
    "creators": [
        {"creator_name": "Florian Angerer", "affiliation": "TU Wien", "name_type": "Personal"},
        {"creator_name": "Swetha Maria Siby", "affiliation": "TU Wien", "name_type": "Personal"},
        {"creator_name": "Nicolas Philipp", "affiliation": "TU Wien", "name_type": "Personal"},
        {"creator_name": "Midhun Suresh Nair", "affiliation": "TU Wien", "name_type": "Personal"}
    ],
    "related_identifiers": []
}

url = f"{endpoint}/api/v1/identifier"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

response = requests.post(
    url,
    headers=headers,
    auth=(username, password),
    json=identifier_payload
)

if response.ok:
    print("PID created successfully via direct API call.")
    print(f"Identifier Data: {response.json()}")
else:
    print(f"Failed to create identifier: {response.status_code}")
    print(f"Response: {response.text}")