import time
from Battery import BatteryManager
from datetime import datetime
import pytz
import os

# タイムゾーン設定
JST = pytz.timezone('Asia/Tokyo')

# バッテリーの設定
max_kwh_capacity = 3.6         # 例: 3.6 KWh の最大容量（必要に応じて変更）
max_charging_power = 3000      # 最大充電電力 (W)
max_discharging_power = 3000   # 最大放電電力 (W)

# BatteryManager のインスタンス
battery_manager = BatteryManager(
    max_kwh_capacity=max_kwh_capacity,
    initial_soc=50,  # 仮の初期値 (実環境では適宜変わる)
    max_charging_power=max_charging_power,
    max_discharging_power=max_discharging_power
)

def log_start(action, log_file):
    """
    充放電を開始したことをログに残す
    """
    timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] Start {action.capitalize()} operation\n"
    with open(log_file, 'a') as f:
        f.write(entry)
    print(entry.strip())

def log_power(action, power, log_file):
    """
    瞬時充放電電力 (W) をログに残す (SoC は出さない)
    """
    timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {action.capitalize()} - Power: {power}W\n"
    with open(log_file, 'a') as f:
        f.write(entry)
    print(entry.strip())

def continuous_charge(log_file):
    """
    無限ループで最大充電し続ける (Ctrl + C で停止)
    """
    log_start("charging", log_file)
    try:
        while True:
            # 瞬時充放電電力を取得
            power_response = battery_manager.try_get(
                battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
            )
            if not power_response or power_response['response_result'] == "NG":
                print("Error retrieving power data. Stopping charging.")
                battery_manager.standby_method()
                break
            
            power = int(power_response['response_value'])
            log_power("charging", power, log_file)
            
            # 最大充電
            battery_manager.charging_method(max_charging_power)
            

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Stopping charging.")
        battery_manager.standby_method()

def continuous_discharge(log_file):
    """
    無限ループで最大放電し続ける (Ctrl + C で停止)
    """
    log_start("discharging", log_file)
    try:
        while True:
            # 瞬時充放電電力を取得
            power_response = battery_manager.try_get(
                battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
            )
            if not power_response or power_response['response_result'] == "NG":
                print("Error retrieving power data. Stopping discharging.")
                battery_manager.standby_method()
                break
            
            power = int(power_response['response_value'])
            log_power("discharging", power, log_file)
            
            # 最大放電
            battery_manager.discharging_method(max_discharging_power)
            
            # 次のループまで待機 (必要に応じて秒数を変更)
            time.sleep(5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Stopping discharging.")
        battery_manager.standby_method()

def main():
    # ログファイルをタイムスタンプ付きで作成
    log_file = f"battery_log_{datetime.now(JST).strftime('%Y%m%d_%H%M%S')}.txt"

    print("Choose an operation:")
    print("1. Continuous charging (no SoC check)")
    print("2. Continuous discharging (no SoC check)")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        continuous_charge(log_file)
    elif choice == "2":
        continuous_discharge(log_file)
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
