import csv
from datetime import datetime
import matplotlib.pyplot as plt

def parse_elapsed_time_to_seconds(t_str):
    # "HH:MM:SS" を秒に変換
    h, m, s = t_str.split(':')
    return int(h)*3600 + int(m)*60 + int(s)

def plot_graphs(csv_file_path):
    times = []
    target_socs = []
    predicted_socs = []
    correct_socs = []
    powers = []

    with open(csv_file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        prev_seconds = 0
        cumulative_offset = 0
        for i, row in enumerate(reader):
            # 実際の列名に合わせて修正
            elapsed_str = row['ElapsedTime']
            current_soc = float(row['CurrentSOC'])      # Correct SOCとして描画
            target_soc = float(row['TargetSOC'])
            predicted_soc = float(row['PredictedSOC'])
            power = float(row['Power'])

            current_seconds = parse_elapsed_time_to_seconds(elapsed_str)

            # 前回より小さくなった＝新サイクル
            if i > 0 and current_seconds < prev_seconds:
                cumulative_offset += prev_seconds

            cumulative_time = current_seconds + cumulative_offset

            times.append(cumulative_time)
            target_socs.append(target_soc)
            predicted_socs.append(predicted_soc)
            correct_socs.append(current_soc)
            powers.append(power)

            prev_seconds = current_seconds

    # グラフ1: SOC系グラフ
    fig1 = plt.figure(figsize=(10, 6))
    ax1 = fig1.add_subplot(111)
    ax1.plot(times, target_socs, label='Target SOC', color='red')
    ax1.plot(times, predicted_socs, label='Predicted SOC', color='blue')
    ax1.plot(times, correct_socs, label='Correct SOC', color='green')
    ax1.set_ylabel('SOC (%)')
    ax1.set_ylim(0, 100)
    ax1.set_title('SOC over Time')
    ax1.legend()
    ax1.grid(True)
    plt.xlabel('Time (seconds)')
    plt.tight_layout()

    # グラフ2: Powerグラフ
    fig2 = plt.figure(figsize=(10, 6))
    ax2 = fig2.add_subplot(111)
    ax2.plot(times, powers, label='Power', color='purple')
    ax2.set_ylabel('Power (W)')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylim(-2400, 2400)
    ax2.set_title('Power over Time')
    ax2.legend()
    ax2.grid(True)
    plt.tight_layout()

    # グラフを表示
    plt.show()

if __name__ == "__main__":
    csv_file_path = r"C:\Users\hayas\Desktop\ソツロン\データ類\実験系\ソツロンで使うやつ\graph_creater\パート１.csv"  # CSVファイルのパスを変更
    plot_graphs(csv_file_path)
