from Battery import BatteryManager
from datetime import datetime
import pytz
import os
import matplotlib.pyplot as plt

# タイムゾーン設定
JST = pytz.timezone('Asia/Tokyo')

# 最大KWh容量、初期SoC値、および最大充放電電力の設定
max_kwh_capacity = 3.6  # 例: 3.6 KWhの最大容量
max_charging_power = 2400  # 最大充電電力（W）
max_discharging_power = 2400  # 最大放電電力（W）
efficiency = 0.95  # 充放電効率（95%）

# BatteryManagerのインスタンスを作成
battery_manager = BatteryManager(
    max_kwh_capacity=max_kwh_capacity,
    initial_soc=100,  # 初期値はSOC_Checkで再取得
    max_charging_power=max_charging_power,
    max_discharging_power=max_discharging_power
)

# 初期化用変数
previous_soc = None
predicted_soc = None

def log_operation_start(action, end_soc, log_file):
    soc_result = battery_manager.SOC_Check()
    if soc_result == "ERROR":
        print("Failed to retrieve current SoC.")
        return

    global previous_soc, predicted_soc
    previous_soc = float(soc_result['RemainingCapacity3'])
    predicted_soc = previous_soc  # 初期予測値を現在のSOCに設定

    timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Starting {action.capitalize()} operation from {previous_soc:.2f}% to {end_soc:.2f}%\n"
    with open(log_file, mode='a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def log_data(action, soc, power, predicted_soc, log_file):
    timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"[{timestamp}] {action.capitalize()} - "
        f"SoC: {soc:.2f}%, Power: {power}W, Predicted SoC: {predicted_soc:.2f}%\n"
    )
    with open(log_file, mode='a') as f:
        f.write(log_entry)
    print(log_entry.strip())

def calculate_predicted_soc(current_soc, power_w, duration_s, efficiency):
    """
    積分的なSOC予測値を計算する関数。
    """
    global previous_soc, predicted_soc

    # SOCが変化した場合、予測値をリセット
    if current_soc != previous_soc:
        predicted_soc = current_soc

    # 予測値を積分的に更新
    delta_kwh = (power_w / 1000) * (duration_s / 3600) * efficiency
    predicted_kwh_capacity = (predicted_soc / 100) * max_kwh_capacity + delta_kwh
    predicted_soc = (predicted_kwh_capacity / max_kwh_capacity) * 100

    # SOCは0～100%に制限
    predicted_soc = max(0, min(100, predicted_soc))

    # 更新したSOCを保存
    previous_soc = current_soc

    return predicted_soc

def range_charge(end_soc, log_file):
    log_operation_start("charging", end_soc, log_file)
    print(f"Charging to {end_soc}%...")
    while True:
        soc_result = battery_manager.SOC_Check()
        if soc_result == "ERROR":
            break
        soc = float(soc_result['RemainingCapacity3'])

        if soc >= end_soc:
            print(f"Target SOC of {end_soc}% reached. Stopping charging.")
            battery_manager.standby_method()  # Set the battery to standby mode
            break

        power_response = battery_manager.try_get(
            battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        )
        if power_response is None or power_response['response_result'] == "NG":
            print("Error occurred while retrieving power data during charging.")
            battery_manager.standby_method()  # Stop charging on error
            break

        power = int(power_response['response_value'])
        predicted_soc = calculate_predicted_soc(soc, power, 30, efficiency)
        log_data("charging", soc, power, predicted_soc, log_file)
        battery_manager.charging_method(max_charging_power)

    print(f"Charging process stopped at {soc:.2f}%. Target was {end_soc}%.")

def range_discharge(end_soc, log_file):
    log_operation_start("discharging", end_soc, log_file)
    print(f"Discharging to {end_soc}%...")
    while True:
        soc_result = battery_manager.SOC_Check()
        if soc_result == "ERROR":
            break
        soc = float(soc_result['RemainingCapacity3'])

        if soc <= end_soc:
            print(f"Target SOC of {end_soc}% reached. Stopping discharging.")
            battery_manager.standby_method()  # Set the battery to standby mode
            break

        power_response = battery_manager.try_get(
            battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        )
        if power_response is None or power_response['response_result'] == "NG":
            print("Error occurred while retrieving power data during discharging.")
            battery_manager.standby_method()  # Stop discharging on error
            break

        power = int(power_response['response_value'])
        predicted_soc = calculate_predicted_soc(soc, power, 30, efficiency)
        log_data("discharging", soc, power, predicted_soc, log_file)
        battery_manager.discharging_method(max_discharging_power)

    print(f"Discharging process stopped at {soc:.2f}%. Target was {end_soc}%.")



def plot_charge_discharge_log_realtime(log_file):
    plt.ion()  # インタラクティブモードをオンに
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    while True:
        timestamps, soc_values, power_values, predicted_soc_values = [], [], [], []

        if not os.path.exists(log_file):
            print(f"Log file {log_file} not found yet. Retrying...")
            plt.pause(5)
            continue

        with open(log_file, 'r') as f:
            for line in f:
                if "SoC" in line and "Power" in line:
                    parts = line.split(" - ")
                    timestamp = parts[0].strip("[]")
                    soc = float(parts[1].split(", ")[0].split(": ")[1].strip("%"))
                    power = int(parts[1].split(", ")[1].split(": ")[1].strip("W"))
                    predicted_soc = float(parts[1].split(", ")[2].split(": ")[1].strip("%"))

                    timestamps.append(timestamp)
                    soc_values.append(soc)
                    power_values.append(power)
                    predicted_soc_values.append(predicted_soc)

        ax1.clear()
        ax2.clear()

        ax1.plot(timestamps, soc_values, marker='o', label="SoC (%)", color="blue")
        ax1.plot(timestamps, predicted_soc_values, marker='x', label="Predicted SoC (%)", linestyle='dashed', color="cyan")
        ax1.set_xlabel("Time")
        ax1.set_ylabel("SoC (%)", color="blue")
        ax1.tick_params(axis='y', labelcolor="blue")
        ax1.set_title("Charge/Discharge Process")

        ax2.plot(timestamps, power_values, marker='o', label="Power (W)", color="red")
        ax2.set_ylabel("Power (W)", color="red")
        ax2.tick_params(axis='y', labelcolor="red")

        fig.autofmt_xdate()
        fig.tight_layout()
        plt.legend(loc="upper left")
        plt.draw()
        plt.pause(5)

def main():
    log_file = f"charge_discharge_log_{datetime.now(JST).strftime('%Y%m%d_%H%M%S')}.txt"
    soc_result = battery_manager.SOC_Check()

    if soc_result == "ERROR":
        print("Failed to retrieve the current SoC. Exiting.")
        return

    print("Choose an operation:")
    print("1. Range charge (e.g., to 80%)")
    print("2. Range discharge (e.g., to 20%)")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice in ["1", "2"]:
        end_soc = float(input("Enter the target SoC (%): ").strip())
        if end_soc < 0 or end_soc > 100:
            print("Invalid SoC range. SoC must be between 0 and 100.")
            return

        if choice == "1":
            range_charge(end_soc, log_file)
        elif choice == "2":
            range_discharge(end_soc, log_file)
    else:
        print("Invalid choice. Exiting.")
        return

    plot_charge_discharge_log_realtime(log_file)

if __name__ == "__main__":
    main()
