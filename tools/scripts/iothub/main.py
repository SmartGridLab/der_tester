import threading
import time
from Battery import BatteryManager
from CSV_Parser import extract_soc_bid_data  # CSV抽出用の関数をインポート
from datetime import datetime
import pytz

# タイムゾーン設定
JST = pytz.timezone('Asia/Tokyo')

# 最大KWh容量、初期SoC値、および最大充放電電力の設定
max_kwh_capacity = 3.6  # 蓄電池の最大容量（KWh）
initial_soc = 80  # 初期のSoC値を80%に設定
max_charging_power = 400  # 最大充電電力（W）
max_discharging_power = 300  # 最大放電電力（W）
efficiency = 0.95  # 充放電効率（95%）

# BatteryManagerのインスタンスを作成
battery_manager = BatteryManager(
    max_kwh_capacity=max_kwh_capacity,
    initial_soc=initial_soc,
    max_charging_power=max_charging_power,
    max_discharging_power=max_discharging_power
)

def log_action_start(action):
    """
    実行内容をログに記録する関数。
    
    Args:
    action (str): 実行するアクション名（"edge" または "smooth"）
    """
    timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Starting {action.capitalize()} Control Mode\n"
    with open('log.txt', mode='a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def calculate_predicted_soc(current_soc, power_w, duration_s, efficiency):
    """
    SOC予測値を計算する関数。
    
    Args:
    current_soc (float): 現在のSOC（%）
    power_w (int): 充放電電力（W）
    duration_s (int): 継続時間（秒）
    efficiency (float): 充放電効率（0～1）
    
    Returns:
    float: 予測SOC（%）
    """
    delta_kwh = (power_w / 1000) * (duration_s / 3600) * efficiency
    new_kwh_capacity = battery_manager.current_kwh_capacity + delta_kwh
    new_soc = (new_kwh_capacity / max_kwh_capacity) * 100
    return max(0, min(100, new_soc))  # SOCは0～100%に制限

def monitor_power_thread():
    """
    モニタリングスレッド。
    SOC予測値を計算し、ログおよび出力。
    """
    while True:
        # 充放電電力を取得
        power_payload = battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        power_response = battery_manager.try_get(power_payload)

        if power_response is None or power_response['response_result'] == "NG":
            print("Error occurred in retrieving power. Monitoring failed.")
            return "ERROR"

        # 現在のSOCを取得
        soc_payload = battery_manager.create_get_payload("remainingCapacity3")
        soc_response = battery_manager.try_get(soc_payload)

        if soc_response is None or soc_response['response_result'] == "NG":
            print("Error occurred in retrieving SoC. Monitoring failed.")
            return "ERROR"

        # 現在の値を取得
        current_power = int(power_response['response_value'])
        current_soc = float(soc_response['response_value'])

        # SOC予測値を計算
        predicted_soc = calculate_predicted_soc(current_soc, current_power, 30, efficiency)

        # 結果を出力およびログ
        timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"[{timestamp}] Current SOC: {current_soc:.2f}%, "
            f"Power: {current_power}W, Predicted SOC: {predicted_soc:.2f}%\n"
        )
        with open('log.txt', mode='a') as f:
            f.write(log_entry)
        print(log_entry.strip())

        # 30秒待機
        time.sleep(30)

def run_controller_edge(soc_bid_data):
    for time_key, soc_bids in soc_bid_data.items():
        soc_bids_float = [float(soc_bid) for soc_bid in soc_bids]
        average_soc_bid = sum(soc_bids_float) / len(soc_bids_float)
        
        soc_result = battery_manager.SOC_Check()
        if soc_result == "ERROR":
            continue
        
        current_soc = float(soc_result['RemainingCapacity3'])
        if current_soc < average_soc_bid:
            battery_manager.charging_method(battery_manager.max_charging_power)
        elif current_soc > average_soc_bid:
            battery_manager.discharging_method(battery_manager.max_discharging_power)
        else:
            battery_manager.standby_method()

def run_controller_smooth(soc_bid_data):
    for time_key, soc_bids in soc_bid_data.items():
        soc_bids_float = [float(soc_bid) for soc_bid in soc_bids]
        average_soc_bid = sum(soc_bids_float) / len(soc_bids_float)
        
        soc_result = battery_manager.SOC_Check()
        if soc_result == "ERROR":
            continue
        
        current_soc = float(soc_result['RemainingCapacity3'])
        soc_difference = average_soc_bid - current_soc
        remaining_time_hours = 1
        required_power = (soc_difference / 100) * battery_manager.max_kwh_capacity / remaining_time_hours * 1000

        if required_power > 0:
            charging_power = min(required_power, battery_manager.max_charging_power)
            battery_manager.charging_method(charging_power)
        elif required_power < 0:
            discharging_power = min(abs(required_power), battery_manager.max_discharging_power)
            battery_manager.discharging_method(discharging_power)
        else:
            battery_manager.standby_method()

# CSVファイルのパスを指定
file_path = '/workspaces/der_tester/tools/scripts/iothub/result_dataframe.csv'
soc_bid_data = extract_soc_bid_data(file_path)

# ユーザーが選択した制御モードに応じて関数を実行
mode = input("Enter control mode ('edge' or 'smooth'): ").strip().lower()

# 実行内容をログに記録
log_action_start(mode)

monitor_thread = threading.Thread(target=monitor_power_thread, daemon=True)
monitor_thread.start()

if mode == 'edge':
    run_controller_edge(soc_bid_data)
elif mode == 'smooth':
    run_controller_smooth(soc_bid_data)
else:
    print("Invalid mode selected. Please choose 'edge' or 'smooth'.")

monitor_thread.join()
