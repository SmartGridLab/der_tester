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
max_charging_power = 2400  # 最大充電電力（W）
max_discharging_power = 2400  # 最大放電電力（W）

# BatteryManagerのインスタンスを作成
battery_manager = BatteryManager(
    max_kwh_capacity=discharging_capacity_kwh,  # 初期値として放電容量を設定
    initial_soc=0,  # 後でログまたは初期値から設定
    max_charging_power=max_charging_power,
    max_discharging_power=max_discharging_power
)

# ログ記録関数
def write_log(log_file, start_time, current_soc, target_soc, predicted_soc, power, status):
    elapsed_time = datetime.now(JST) - start_time
    elapsed_hours = elapsed_time.seconds // 3600
    elapsed_minutes = (elapsed_time.seconds % 3600) // 60
    elapsed_seconds = elapsed_time.seconds % 60
    elapsed = f"{elapsed_hours:02}:{elapsed_minutes:02}:{elapsed_seconds:02}"

    with open(log_file, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([elapsed, current_soc, target_soc, predicted_soc, power, status])

# 積分的にSOC予測値を計算する関数
def calculate_predicted_soc(current_soc, power_w, elapsed_time_seconds, previous_predicted_soc):
    max_capacity = charging_capacity_kwh if power_w > 0 else discharging_capacity_kwh
    previous_kwh = (previous_predicted_soc / 100) * max_capacity
    delta_kwh = (power_w * elapsed_time_seconds) / (3600 * 1000)  # kWh単位に変換
    new_kwh = previous_kwh + delta_kwh
    new_soc = (new_kwh / max_capacity) * 100
    return max(0, min(100, new_soc))

def run_controller_smooth(soc_bid_list, log_file, start_time):
    predicted_soc = 0.0  # 初期予測SOC
    last_log_time = start_time

    for index, soc_bid in enumerate(soc_bid_list):
        target_soc = soc_bid['soc_bid']
        duration_s = 1800  # 30分間の制御サイクル

        # --- 30分サイクル開始時に一度だけ計算と設定を行う ---
        # 現在のSOCとパワー取得
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

        # 情報がすべて揃った時点の時刻で経過時間を計算
        now_time = datetime.now(JST)
        elapsed_time_seconds = (now_time - last_log_time).total_seconds()

        # 予測SOC更新
        predicted_soc = calculate_predicted_soc(current_soc, power, elapsed_time_seconds, predicted_soc)

        # 必要な充放電電力をサイクル開始時に決定
        soc_difference = target_soc - predicted_soc
        if soc_difference > 0:
            # 充電が必要
            required_power = round((soc_difference / 100) * charging_capacity_kwh * 1000 / (duration_s / 3600))
            battery_manager.charging_method(required_power)
            status = "Charging"
        elif soc_difference < 0:
            # 放電が必要
            required_power = round((abs(soc_difference) / 100) * discharging_capacity_kwh * 1000 / (duration_s / 3600))
            battery_manager.discharging_method(required_power)
            status = "Discharging"
        else:
            # 差が0なら待機
            required_power = 0
            battery_manager.standby_method()
            status = "Standby"

        cycle_start_time = datetime.now(JST)
        # ログ出力（既に情報は取得済み、elapsed_time_seconds算出済み）
        write_log(log_file, start_time, current_soc, target_soc, predicted_soc, power, status)
        last_log_time = cycle_start_time  # ログ記録後の時刻をlast_log_timeに

        # --- 小ループ開始（約20秒ごと） ---
        standby_mode_engaged = False  # 目標達成後一度だけstandbyを送るためのフラグ
        while True:
            # 現在のSOCを取得
            soc_result = battery_manager.SOC_Check()
            if soc_result == "ERROR":
                time.sleep(5)
                continue
            current_soc = float(soc_result['RemainingCapacity3'])

            # 実際の充放電電力を1回だけ取得
            power_response = battery_manager.try_get(
                battery_manager.create_get_payload("instantaneousChargingAndDischargingElectricPower")
            )
            if power_response is None or power_response['response_result'] == "NG":
                print("Error: Unable to fetch power.")
                time.sleep(5)
                continue
            power = int(power_response['response_value'])

            # 全情報取得後の時刻
            now_time = datetime.now(JST)
            elapsed_time_seconds = (now_time - last_log_time).total_seconds()

            # 予測SOC更新（観測値power使用）
            predicted_soc = calculate_predicted_soc(current_soc, power, elapsed_time_seconds, predicted_soc)

            # 目標SOC達成判定
            if predicted_soc >= target_soc:
                # 一度だけStandbyを送る（まだ送っていなければ）
                if not standby_mode_engaged:
                    battery_manager.standby_method()
                    status = "Standby"
                    standby_mode_engaged = True
                else:
                    # すでにStandby中ならモード変更は不要
                    status = "Standby"
            # 目標未達ならstatusは前サイクルのまま(ChargingやDischargingのまま)

            # ログ書き込み
            write_log(log_file, start_time, current_soc, target_soc, predicted_soc, power, status)
            last_log_time = datetime.now(JST)

            # 30分経過で次のサイクルへ
            if (datetime.now(JST) - cycle_start_time).total_seconds() >= duration_s:
                # 次のSOCビッドへ
                if index + 1 < len(soc_bid_list):
                    start_time = datetime.now(JST)
                break

            time.sleep(5)

# CSVファイルからSOCビッドデータを抽出
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

# ログファイルから最新SOCを取得
def get_last_soc_from_log(log_file):
    try:
        with open(log_file, mode='r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # ヘッダーをスキップ
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                return float(last_row[1])  # 現在のSOCを取得 (Current SOCは2列目)
    except Exception as e:
        print(f"Error reading log file: {e}")
    return None

# メイン関数
def main():
    file_path = '/workspaces/der_tester/tools/scripts/iothub/result_dataframe.csv'
    soc_bid_list = extract_soc_bid_data(file_path)

    log_file = input("Enter log file path (or press Enter to start a new log): ").strip()
    if log_file:
        last_soc = get_last_soc_from_log(log_file)
        if last_soc is not None:
            print(f"Resuming from SOC: {last_soc}%")
            battery_manager.set_initial_soc(last_soc)
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
