import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ['TARGET_URL']

def getting(getvalue):
   payload_get = {
       "requests": [
           {
               "command": [
                   {
                       "command_type": "character",
                       "command_code": "get_property_value",
                       "command_value": getvalue
                   }
               ],
               "driver_id": os.environ['DRIVER_ID'],
               "r_edge_id": os.environ['R_EDGE_ID'],
               "thing_uuid": os.environ['THING_UUID']
           }
       ]
   }
   return payload_get

headers = {
   "Content-type": "application/json",
   "Authorization": "Bearer " + os.environ['ACCESS_TOKEN'],
   "X-IOT-API-KEY": os.environ['API_KEY']
}

def check_remaining_capacity():
   payload_get = getting("remainingCapacity3")
   try:
       response = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
       json_data = response.json()
       for result in json_data['results']:
           for command in result["command"]:
               for response in command["response"]:
                   if response["response_result"] == "OK":
                       remaining_capacity = response["response_value"]
                       print(f"{remaining_capacity}")
                   else:
                       print("Error getting remaining capacity.")
   except TimeoutError:
       print("Timeout error occurred.")

# Call the function
check_remaining_capacity()