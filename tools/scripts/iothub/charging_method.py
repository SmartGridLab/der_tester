#
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

get1 = None
#try_get,try_setの関数
def try_get():
    global get1
    get1 = None
    try:
        response_get1 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
        print(response_get1.text)
        jsonData = response_get1.json()
        for result in reversed(jsonData['results']):
            for command in reversed(result["command"]):
                for response in reversed(command["response"]):
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
        for result in reversed(jsonData['results']):
            for command in reversed(result["command"]):
                for response in reversed(command["response"]):
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


#実際にget,setを入れるところ 例：
#payload_get=getting("instantaneousChargingAndDischargingElectricPower")
# payload_set=setting("operationMode=standby")

#実行内容 例：（set,getは各１回まで）
#try_get()
#try_set()

#実際にget,setを入れるところ
payload_get=getting("instantaneousChargingAndDischargingElectricPower")
#実行内容（set,getは各１回まで）

#電力取得NGの場合
try_get()
if  get1['response_result']=="NG":
    print("Getting_Electric_Power_error")
#電力取得OKの場合。
else : 
    print("Getting_Electric_Power_success")
    Electric_Power = int(get1['response_value'])
    if Electric_Power >=1: #電力が1以上の場合の分岐
        payload_get=getting("operationMode")
        try_get()
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
        else:
            print("Getting_OperationMode_success")
            if get1['response_value']=="charging":
                print("already_charging")
            elif get1['response_value']=="discharging":
                print("unexpected_charging(discharging_setting)")
            elif get1['response_value']=="standby" or "auto":
                print("unexpected_charging(standby_setting)")
        
    elif Electric_Power<=-1: #電力が-1以下の場合の分岐
        payload_get=getting("operationMode")
        try_get()
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
        else:
            
            if get1['response_value'] == "charging":
                print("unexpected_discharging(charging_setting)")
            elif get1['response_value'] == "standby":
                print("unexpected_discharging(standby_setting)")
            else:
                payload_get = getting("remainingCapacity3")
                try_get()
                if get1['response_result'] == "NG":
                    print("Getting_RemainingCapacity3_error")
                else:
                    print("Getting_RemainingCapacity3_success")
                    RemainingCapacity3 = int(get1['response_value'])
                    if RemainingCapacity3 <= 90:
                        # ここからが本来の動き
                        #payload_set = setting("operationMode=charging")
                        #try_set()
                        #if get1['response_result'] == "NG":
                        #    print("Setting_OperationMode_error")
                        #else:
                        #    print("Setting_OperationMode_success")
                        #time.sleep(20)
                        #payload_get = getting("instantaneousChargingAndDischargingElectricPower")
                        #try_get()
                        #Electric_Power = int(get1['response_value'])
                        #if Electric_Power >= 1:
                        #    print("Charging_success")
                        #else:
                        #    print("charging_error")
                        # ここまでが本来の動き

                        # ここからが一時的な処置。2分待つ。この間に実機の操作をする。
                        print("1min_waiting")
                        time.sleep(60)
                        payload_get = getting("operationMode")  # 実機操作後のモード取得。
                        try_get()
                        # response_valueがchargingになっていれば、成功を出す。
                        if get1["command_value"] == "charging" or "auto":
                            print("Setting_OperationMode_success")
                            time.sleep(20)
                            payload_get = getting("instantaneousChargingAndDischargingElectricPower")
                            try_get()
                            Electric_Power = int(get1['response_value'])
                            if Electric_Power >= 1:
                                print("Charging_success")
                            else:
                                print("charging_error")
                        else:
                            print("Setting_OperationMode_error")
                    else:
                        print("too_much_remainingCapacity3(dischaging_setting)")
            
           
    else:#電力が0の場合の分岐
        payload_get=getting("operationMode")
        try_get()
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
        else:
            print("Getting_OperationMode_success")
            if get1['response_value']=="charging":
                print("cannot_charge")
            elif get1['response_value']=="discharging":
                print("cannot_discharge")
            elif get1['response_value']=="standby" or "auto":
                payload_get=getting("remainingCapacity3")
                try_get()
                if get1['response_result']=="NG":
                    print("Getting_RemainingCapacity3_error")
                else:
                    print("Getting_RemainingCapacity3_success")
                    RemainingCapacity3 = int(get1['response_value'])
                    if RemainingCapacity3<=95:
                        #2分待つ。この間に実機の操作をする。
                        print("1min_waiting")
                        time.sleep(60)
                        #ここから本来の動き
                        #payload_set=setting("operationMode=charging")
                        #try_set()
                        #if 'response_result'=="NG":
                            #print("Setting_OperationMode_error")
                        #else:
                            #print("Setting_OperationMode_success")
                        payload_get=getting("operationMode") #実機操作後のモード取得。
                        try_get()
                        #response_valueがchargingになっていれば、成功を出す。
                        if get1['response_value']=="charging" or "auto":
                            print("Setting_OperationMode_success")
                            time.sleep(20)
                            payload_get=getting("instantaneousChargingAndDischargingElectricPower")
                            try_get()
                            Electric_Power = int(get1['response_value'])
                            if Electric_Power>=1:
                                print("Charging_success")
                            else:
                                print("charging_error")
                        else:
                            print("Setting_OperationMode_error")
                    else:
                        print("too_much_remainingCapacity3(standby_setting)")
        
