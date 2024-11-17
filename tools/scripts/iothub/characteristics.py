#充放電特性を求めるコード
from Battery import BatteryManager
from datetime import datetime

# 最大KWh容量、初期SoC値、および最大充放電電力の設定
max_kwh_capacity = 4.2  # 例: 4.2 KWhの最大容量
initial_soc = 0  # 初期のSoC値
max_charging_power = 400  # 最大充電電力（W）
max_discharging_power = 300  # 最大放電電力（W）

# BatteryManagerのインスタンスを作成
battery_manager = BatteryManager(
    max_kwh_capacity=max_kwh_capacity,
    initial_soc=initial_soc,
    max_charging_power=max_charging_power,
    max_discharging_power=max_discharging_power
)

def log_operation_start(action):
    """
    操作の開始をログに記録する関数。
    
    Args:
    action (str): "charging" または "discharging" の操作名
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Starting {action.capitalize()} operation\n"
    with open('charge_discharge_log.txt', mode='a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def log_data(action, soc, power):
    """
    ログデータを記録する関数。
    
    Args:
    action (str): "charging" または "discharging" のアクション名
    soc (float): 現在のSoC値（%）
    power (int): 現在の充放電電力（W）
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action.capitalize()} - SoC: {soc:.2f}%, Power: {power}W\n"
    with open('charge_discharge_log.txt', mode='a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def full_charge():
    """
    0%から100%まで充電を行う関数。
    """
    log_operation_start("charging")
    print("Starting full charge test...")
    while battery_manager.current_soc < 100:
        power_payload = battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        power_response = battery_manager.try_get(power_payload)
        if power_response is None or power_response['response_result'] == "NG":
            print("Error occurred while retrieving power data during charging.")
            break
        
        soc = battery_manager.current_soc
        power = int(power_response['response_value'])
        
        # SoCと電力をログ
        log_data("charging", soc, power)
        
        # 充電を続行
        battery_manager.charging_method(max_charging_power)

    print("Full charge test completed.")

def full_discharge():
    """
    100%から0%まで放電を行う関数。
    """
    log_operation_start("discharging")
    print("Starting full discharge test...")
    while battery_manager.current_soc > 0:
        power_payload = battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        power_response = battery_manager.try_get(power_payload)
        if power_response is None or power_response['response_result'] == "NG":
            print("Error occurred while retrieving power data during discharging.")
            break
        
        soc = battery_manager.current_soc
        power = int(power_response['response_value'])
        
        # SoCと電力をログ
        log_data("discharging", soc, power)
        
        # 放電を続行
        battery_manager.discharging_method(max_discharging_power)

    print("Full discharge test completed.")

def main():
    """
    ユーザーに充放電プロセスを選択させるメイン関数。
    """
    print("Choose an operation:")
    print("1. Full charge (0% to 100%)")
    print("2. Full discharge (100% to 0%)")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        full_charge()
    elif choice == "2":
        full_discharge()
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
