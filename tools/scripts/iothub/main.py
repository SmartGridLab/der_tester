import threading
import time
import csv
from Battery import BatteryManager
from datetime import datetime, timedelta
import pytz

# タイムゾーン設定
JST = pytz.timezone('Asia/Tokyo')

# 設定値
charging_capacity_kwh = 4.4  # 充電時の実測容量 (kWh)
discharging_capacity_kwh = 3.7  # 放電時の実測容量 (kWh)
max_charging_power = 2500  # 最大充電電力(W)
max_discharging_power = 2500  # 最大放電電力(W)


battery_manager = BatteryManager(
    max_kwh_capacity=discharging_capacity_kwh,
    max_charging_power=max_charging_power,
    max_discharging_power=max_discharging_power,
    initial_soc=21)

def write_log(log_file, start_time, current_soc, target_soc, predicted_soc, power, status):
    elapsed_time = datetime.now(JST) - start_time
    elapsed_hours = elapsed_time.seconds // 3600
    elapsed_minutes = (elapsed_time.seconds % 3600) // 60
    elapsed_seconds = elapsed_time.seconds % 60
    elapsed = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

    with open(log_file, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([elapsed, current_soc, target_soc, predicted_soc, power, status])

def calculate_predicted_soc(current_soc, power_w, elapsed_time_seconds, previous_predicted_soc):
    max_capacity = charging_capacity_kwh if power_w > 0 else discharging_capacity_kwh
    previous_kwh = (previous_predicted_soc / 100) * max_capacity
    delta_kwh = (power_w * elapsed_time_seconds) / (3600 * 1000)
    new_kwh = previous_kwh + delta_kwh
    new_soc = (new_kwh / max_capacity) * 100
    return max(0, min(100, new_soc))

def run_controller_smooth(soc_bid_list, log_file, start_time):
    predicted_soc = battery_manager.initial_soc
    last_log_time = start_time

    for index, soc_bid in enumerate(soc_bid_list):
        target_soc = soc_bid['soc_bid']
        duration_s = 1800  # 30分

        # サイクル開始時に1回計算
        soc_result = battery_manager.SOC_Check()
        if soc_result == "ERROR":
            continue
        current_soc = float(soc_result['RemainingCapacity3'])

        power_response = battery_manager.try_get(
            battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
        )
        if power_response is None or power_response['response_result'] == "NG":
            print("Error: Unable to fetch power.")
            continue
        power = int(power_response['response_value'])

        now_time = datetime.now(JST)
        elapsed_time_seconds = (now_time - last_log_time).total_seconds()

        predicted_soc = calculate_predicted_soc(current_soc, power, elapsed_time_seconds, predicted_soc)

        soc_difference = target_soc - predicted_soc

        # 0.5%以下なら充放電せず30分間Standby
        if abs(soc_difference) <= 0.5:
            # Standby状態で30分過ごす
            battery_manager.standby_method()
            operation_mode = "Standby"
            status = "Standby"
            required_power = 0
        else:
            # 従来通り充放電を決定
            if soc_difference > 0:
                required_power = round((soc_difference / 100) * charging_capacity_kwh * 1000 / (duration_s / 3600))
                battery_manager.charging_method(required_power)
                operation_mode = "Charging"
                status = "Charging"
            elif soc_difference < 0:
                required_power = round((abs(soc_difference) / 100) * discharging_capacity_kwh * 1000 / (duration_s / 3600))
                battery_manager.discharging_method(required_power)
                operation_mode = "Discharging"
                status = "Discharging"
            else:
                required_power = 0
                battery_manager.standby_method()
                operation_mode = "Standby"
                status = "Standby"

        cycle_start_time = datetime.now(JST)
        write_log(log_file, start_time, current_soc, target_soc, predicted_soc, power, status)
        last_log_time = cycle_start_time

        standby_mode_engaged = False
        last_known_battery_soc = current_soc

        # 小ループ
        while True:
            soc_result = battery_manager.SOC_Check()
            if soc_result == "ERROR":
                time.sleep(5)
                continue
            current_soc = float(soc_result['RemainingCapacity3'])

            power_response = battery_manager.try_get(
                battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
            )
            if power_response is None or power_response['response_result'] == "NG":
                print("Error: Unable to fetch power.")
                time.sleep(5)
                continue
            power = int(power_response['response_value'])

            now_time = datetime.now(JST)
            elapsed_time_seconds = (now_time - last_log_time).total_seconds()

            # CurrentSOCに変化があった場合、PredictedSOCをCurrentSOCに合わせる
            if current_soc != last_known_battery_soc:
                predicted_soc = current_soc
            else:
                predicted_soc = calculate_predicted_soc(current_soc, power, elapsed_time_seconds, predicted_soc)

            last_known_battery_soc = current_soc

            # 0.5%以下でStandbyの場合、あるいは既に目標達成でStandby中なら特に充放電はしない
            if operation_mode == "Standby":
                # 常にStandby
                status = "Standby"
            else:
                # 目標SOC達成判定
                if operation_mode == "Charging":
                    if predicted_soc >= target_soc:
                        if not standby_mode_engaged:
                            battery_manager.standby_method()
                            status = "Standby"
                            standby_mode_engaged = True
                        else:
                            status = "Standby"
                    else:
                        status = "Charging"
                elif operation_mode == "Discharging":
                    if predicted_soc <= target_soc:
                        if not standby_mode_engaged:
                            battery_manager.standby_method()
                            status = "Standby"
                            standby_mode_engaged = True
                        else:
                            status = "Standby"
                    else:
                        status = "Discharging"

            write_log(log_file, start_time, current_soc, target_soc, predicted_soc, power, status)
            last_log_time = datetime.now(JST)

            # 30分経過
            if (datetime.now(JST) - cycle_start_time).total_seconds() >= duration_s:
                if index + 1 < len(soc_bid_list):
                    start_time = datetime.now(JST)
                break

            time.sleep(5)

def extract_soc_bid_data(file_path):
    soc_bid_list = []
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            soc_bid_list.append({
                'hour': int(row['hour']),
                'minute': int(row['minute']),
                'soc_bid': float(row['SoC'])
            })
    return soc_bid_list

def get_last_soc_from_log(log_file):
    try:
        with open(log_file, mode='r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                return float(last_row[1])
    except Exception as e:
        print(f"Error reading log file: {e}")
    return None

def main():
    file_path = r'/workspaces/der_tester/tools/scripts/iothub/Part3.csv'
    soc_bid_list = extract_soc_bid_data(file_path)

    log_file = input("Enter log file path (or press Enter to start a new log): ").strip()
    if log_file:
        last_soc = get_last_soc_from_log(log_file)
        if last_soc is not None:
            print(f"Resuming from SOC: {last_soc}%")
            battery_manager.initial_soc =last_soc
        else:
            print("Log file is empty or unreadable. Starting from initial SOC.")
            log_file = f"log_{datetime.now(JST).strftime('%Y%m%d_%H%M%S')}.csv"
    else:
        log_file = f"log_{datetime.now(JST).strftime('%Y%m%d_%H%M%S')}.csv"

    with open(log_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Elapsed Time", "Current SOC", "Target SOC", "Predicted SOC", "Power", "Status"])

    start_time = datetime.now(JST)
    run_controller_smooth(soc_bid_list, log_file, start_time)

if __name__ == "__main__":
    main()
