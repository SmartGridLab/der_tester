import matplotlib.pyplot as plt
import time
import os

def parse_log_line(line):
    """
    ログの1行を解析してデータを抽出する関数。

    Args:
    line (str): ログの1行

    Returns:
    tuple: (timestamp, soc, power, predicted_soc) または None（パースできない場合）
    """
    try:
        parts = line.split(" - ")
        timestamp = parts[0].strip("[]")
        soc = float(parts[1].split(", ")[0].split(": ")[1].strip("%"))
        power = int(parts[1].split(", ")[1].split(": ")[1].strip("W"))
        predicted_soc = float(parts[1].split(", ")[2].split(": ")[1].strip("%\n"))
        return timestamp, soc, power, predicted_soc
    except Exception as e:
        print(f"Error parsing line: {line.strip()}. Error: {e}")
        return None

def plot_log_realtime(log_file):
    """
    ログファイルをリアルタイムで読み込み、グラフを更新する関数。

    Args:
    log_file (str): ログファイルのパス
    """
    timestamps = []
    soc_values = []
    power_values = []
    predicted_soc_values = []

    plt.ion()  # インタラクティブモードをオンに
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    # 最後に読み取った位置を記録
    last_position = 0

    while True:
        # ファイルが存在しない場合、再試行
        if not os.path.exists(log_file):
            print(f"Log file {log_file} not found. Retrying...")
            time.sleep(5)
            continue

        with open(log_file, 'r') as f:
            # 前回の読み取り位置にシーク
            f.seek(last_position)

            # 新しい行を読み込む
            new_lines = f.readlines()
            last_position = f.tell()

        # 新しいデータを解析して追加
        for line in new_lines:
            parsed_data = parse_log_line(line)
            if parsed_data:
                timestamp, soc, power, predicted_soc = parsed_data
                timestamps.append(timestamp)
                soc_values.append(soc)
                power_values.append(power)
                predicted_soc_values.append(predicted_soc)

        # グラフを更新
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
        plt.pause(5)  # 5秒ごとに更新

if __name__ == "__main__":
    # ログファイルのパスを指定
    log_file_path = input("Enter the path to the log file: ").strip()

    if not os.path.exists(log_file_path):
        print(f"Log file {log_file_path} not found.")
    else:
        plot_log_realtime(log_file_path)
