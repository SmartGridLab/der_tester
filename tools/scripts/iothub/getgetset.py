# コマンドをセットする手順のところを関数にすることで可読性が高くなると同時に、１回の実行で複数のget/setをすることが容易になりました

import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys

load_dotenv()

url = os.environ['TARGET_URL']


# getの関数
def  getting(getvalue):
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



#setの関数
def setting(setvalue):
  payload_set = {
   "requests": [
     {
       "command": [
         {
         "command_type": "character", 
         "command_code": "set_property_value",
         "command_value": setvalue}
       ],

       "driver_id": os.environ['DRIVER_ID'],
       "r_edge_id": os.environ['R_EDGE_ID'],
       "thing_uuid": os.environ['THING_UUID']
      } 
    ]
  }
  return payload_set

headers = {
  "Content-type": "application/json",
  "Authorization": "Bearer "+os.environ['ACCESS_TOKEN'],
  "X-IOT-API-KEY": os.environ['API_KEY']
}

#try_get,try_setの関数
def try_get():
    try:
        response_get1 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
        print(response_get1.text)
        jsonData = response_get1.json()
        for result in jsonData['results']:
            for command in result["command"]:
                for response in command["response"]:
                    get1 = {
                        'command_code': command["command_code"],
                        'command_value': command["command_value"],
                        'response_result': response["response_result"],
                        'response_value': response["response_value"]
                    }
                    print(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})")
                    #print()の中身をtxtファイルに書き込む
                    with open('log.txt', mode='a') as f:
                        f.write(f"{get1['command_code']} ({get1['command_value']}) ... {get1['response_result']} ({get1['response_value']})\n")
    except TimeoutError:
        print("get1 is timed out")   
        #print()の中身をtxtファイルに書き込む
        with open('log.txt', mode='a') as f:
            f.write("get1 is timed out\n")    
        pass
        time.sleep(5)
  
def try_set():
    try:
        response_get1 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
        print(response_get1.text)
        jsonData = response_get1.json()
        for result in jsonData['results']:
            for command in result["command"]:
                for response in command["response"]:
                    set1 = {
                        'command_code': command["command_code"],
                        'command_value': command["command_value"],
                        'response_result': response["response_result"],
                        'response_value': response["response_value"]
                    }
                    print(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})")
                    #print()の中身をtxtファイルに書き込む
                    with open('log.txt', mode='a') as f:
                        f.write(f"{set1['command_code']} ({set1['command_value']}) ... {set1['response_result']} ({set1['response_value']})\n")
    except TimeoutError:
        print("set1 is timed out")
        #print()の中身をtxtファイルに書き込む
        with open('log.txt', mode='a') as f:
            f.write("set1 is timed out\n")
        pass
        time.sleep(5)


#実際にget,setを入れるところ
payload_get=getting("instantaneousChargingAndDischargingElectricPower")
payload_set=setting("operationMode=standby")

#実行内容（set,getは各１回まで）
try_get()
try_set()

#実際にget,setを入れるところ
payload_get=getting("instantaneousChargingAndDischargingCurrent")
time.sleep(5)
#実行内容（set,getは各１回まで）
try_get()
