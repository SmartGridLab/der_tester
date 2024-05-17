#放電に設定するコード

#元のコードからimportなどの部分を流用
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

#実際にget, setを入れるところ
payload_get=getting("instantaneousChargingAndDischargingElectricPower")
#実行内容（set, getは各１回まで）
try_get()
#電力取得NGの場合
if 'response_result'=="NG":
    print("Getting_Electric_Power_error")
    return "ERROR"
#電力取得OKの場合
else:
    print("Getting_Electric_Power_success")
    Electric_Power = int(get1['response_value'])
    if Electric_Power<=-1: #電力が-1以下の場合の分岐
        payload_get=getting("operationMode")
        try_get()
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
            return "ERROR"
        else:
            print("Getting_OperationMode_success")
            if get1['response_value']=="discharging":
                print("already_discharging")
                return "ERROR"
            elif get1['response_value']=="charging":
                print("unexpected_discharging(charging_setting)")
                return "ERROR"
            elif get1['response_value']=="standby" or "auto":
                print("unexpected_discharging(standby_setting)")
                return "ERROR"

    elif Electric_Power>=1: #電力が1以上の場合の分岐
        payload_get=getting("operationMode")
        try_get()
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
            return "ERROR"
        else:
            print("Getting_OperationMode_success")
            if get1['response_value']=="discharging":
                print("unexpected_charging(discharging_setting)")
                return "ERROR"
            elif get1['response_value']=="standby":
                print("unexpected_charging(standby_setting)")
                return "ERROR"
            else:
                payload_get=getting("remainingCapacity3")
                try_get()
                if get1['response_result']=="NG":
                    print("Getting_RemainingCapacity3_error")
                    return "ERROR"
                else:
                    print("Getting_RemainingCapacity3_success")
                    RemainingCapacity3 = int(get1['response_value'])
                    if RemainingCapacity3>=20: #残量が20%以上の場合に放電
                        #ここから実際の動き
                        #payload_set=setting("operationMode=discharging")
                        #try_set()
                        #if 'response_result'=="NG":
                            #print("Setting_OperationMode_error")
                        #else:
                            #print("Setting_OperationMode_success")
                        #1分待つ。この間に実機操作
                        print("waiting_1min")
                        time.sleep(60)
                        payload_get=getting("operationMode")
                        try_get()
                        #response_valueがdischargingになっていれば、成功を出す。
                        if get1['response_value']=="discharging" or "auto":
                            print("setting_operationMode_success")
                            time.sleep(20)
                            payload_get=getting("instantaneousChargingAndDischargingElectricPower")
                            try_get()
                            Electric_Power = int(get1['response_value'])
                            if Electric_Power<=-1:
                                print("disCharging_success")
                                if get1['response_value'] == "charging":
                                    return "CD01"
                                else:
                                    return "SD01"
                            else:
                                print("discharging_error")
                                return "ERROR"
                        else:
                            print("setting_operationMode_failed")
                            return "ERROR"
                    else:
                        print("too_little_remainingCapacity3")
                        return "ERROR"

    else: #電力が0の場合の分岐
        payload_get=getting("operationMode")
        try_get()
        if get1['response_result']=="NG":
            print("Getting_OperationMode_error")
            return "ERROR"
        else:
            print("Getting_OperationMode_success")
            if get1['response_value']=="charging":
                print("cannot_discharge")
                return "ERROR"
            elif get1['response_value']=="discharging":
                print("cannot_discharge")
                return "ERROR"
            else:
                payload_get=getting("remainingCapacity3")
                try_get()
                if get1['response_result']=="NG":
                    print("Getting_RemainingCapacity3_error")
                    return "ERROR"
                else:
                    print("Getting_RemainingCapacity3_success")
                    RemainingCapacity3 = int(get1['response_value'])
                    if RemainingCapacity3>=20: #残量が20%以上の場合に放電
                        #ここから本来の動き
                        #payload_set=setting("operationMode=discharging")
                        #try_set()
                        #if 'response_result'=="NG":
                            #print("Setting_OperationMode_error")
                        #else:
                            #print("Setting_OperationMode_success")
                        print("waiting_1min")
                        time.sleep(60)
                        payload_get=getting("operationMode")
                        try_get()
                        #response_valueがdischargingになっていれば、成功を出す。
                        if get1['response_value']=="discharging" or "auto":
                            print("setting_operationMode_success")
                            time.sleep(20)
                            payload_get=getting("instantaneousChargingAndDischargingElectricPower")
                            try_get()
                            Electric_Power = int(get1['response_value'])
                            if Electric_Power<=-1:
                                print("disCharging_success")
                                return "SD01"
                            else:
                                print("discharging_error")
                                return "ERROR"
                        else:
                            print("setting_operationMode_failed")
                            return "ERROR"
                    else:
                        print("too_little_remainingCapacity3")
                        return "ERROR"
