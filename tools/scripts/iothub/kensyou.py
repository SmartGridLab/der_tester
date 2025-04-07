import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys
import pytz

# .envファイルの読み込み
load_dotenv()

# TARGET_URLの取得
url = os.environ['TARGET_URL']

# JSTタイムゾーンの設定
JST = pytz.timezone('Asia/Tokyo')

# ログファイルの名前を生成する関数（日時に「時・分」も含む）
def get_log_filename():
    now = datetime.datetime.now(JST)
    # 例："2025-03-22_14-30.txt"
    base_filename = now.strftime("%Y-%m-%d_%H-%M")
    filename = base_filename + ".txt"
    count = 1
    # 同名のファイルがあれば連番でファイル名を変更
    while os.path.exists(filename):
        count += 1
        filename = f"{base_filename}({count}).txt"
    return filename

# ログファイル名を実行毎に決定
log_filename = get_log_filename()

# ログ出力用のヘルパー関数
def log_message(message):
    timestamp = datetime.datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S")
    with open(log_filename, mode='a') as f:
        f.write(f"{timestamp} {message}\n")

# getのpayloadを作成する関数
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

# setのpayloadを作成する関数
def setting(setvalue):
    payload_set = {
        "requests": [
            {
                "command": [
                    {
                        "command_type": "character",
                        "command_code": "set_property_value",
                        "command_value": setvalue
                    }
                ],
                "driver_id": os.environ['DRIVER_ID'],
                "r_edge_id": os.environ['R_EDGE_ID'],
                "thing_uuid": os.environ['THING_UUID']
            }
        ]
    }
    return payload_set

# requestのheadersを決定
headers = {
    "Content-type": "application/json",
    "Authorization": "Bearer " + os.environ['ACCESS_TOKEN'],
    "X-IOT-API-KEY": os.environ['API_KEY']
}

# try_get: 送信前に送ったコマンド値をログに記録、エラー時もその情報を出力
def try_get():
    global get1
    get1 = None
    # payload_getから送信するコマンド値を取得
    input_command = payload_get["requests"][0]["command"][0]["command_value"]
    log_message(f"Sending get command: {input_command}")
    try:
        response_get1 = requests.request("POST", url, headers=headers, json=payload_get, timeout=200)
        print(response_get1.text)
        jsonData = response_get1.json()
        # 逆順に結果を処理
        for result in reversed(jsonData['results']):
            for command in reversed(result["command"]):
                for response in reversed(command["response"]):
                    get1 = {
                        'command_code': command["command_code"],
                        'command_value': command["command_value"],
                        'response_result': response["response_result"],
                        'response_value': response["response_value"]
                    }
                    log_str = (f"Sent command: {input_command} | Received: "
                               f"{get1['command_code']} ({get1['command_value']}) ... "
                               f"{get1['response_result']} ({get1['response_value']})")
                    print(log_str)
                    print(datetime.datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S"))
                    log_message(log_str)
    except TimeoutError:
        error_msg = f"get1 is timed out. Sent command: {input_command}"
        print(error_msg)
        log_message(error_msg)
        time.sleep(5)
    except Exception as e:
        error_msg = f"Error in try_get. Sent command: {input_command} | Error: {str(e)}"
        print(error_msg)
        log_message(error_msg)
        time.sleep(5)

# try_set: 送信前に送ったコマンド値をログに記録、エラー時もその情報を出力
def try_set():
    # payload_setから送信するコマンド値を取得
    input_command = payload_set["requests"][0]["command"][0]["command_value"]
    log_message(f"Sending set command: {input_command}")
    try:
        response_set1 = requests.request("POST", url, headers=headers, json=payload_set, timeout=200)
        print(response_set1.text)
        jsonData = response_set1.json()
        for result in reversed(jsonData['results']):
            for command in reversed(result["command"]):
                for response in reversed(command["response"]):
                    set1 = {
                        'command_code': command["command_code"],
                        'command_value': command["command_value"],
                        'response_result': response["response_result"],
                        'response_value': response["response_value"]
                    }
                    log_str = (f"Sent command: {input_command} | Received: "
                               f"{set1['command_code']} ({set1['command_value']}) ... "
                               f"{set1['response_result']} ({set1['response_value']})")
                    print(log_str)
                    print(datetime.datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S"))
                    log_message(log_str)
    except TimeoutError:
        error_msg = f"set1 is timed out. Sent command: {input_command}"
        print(error_msg)
        log_message(error_msg)
        time.sleep(5)
    except Exception as e:
        error_msg = f"Error in try_set. Sent command: {input_command} | Error: {str(e)}"
        print(error_msg)
        log_message(error_msg)
        time.sleep(5)

# 現在時刻をJSTで表示
print(datetime.datetime.now(JST).strftime("%Y/%m/%d %H:%M:%S"))

#payload_get = getting("operationMode")
#try_get()


payload_set = setting("operationMode=standby")
try_set()
