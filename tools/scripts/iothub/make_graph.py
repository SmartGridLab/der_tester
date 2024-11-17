import matplotlib.pyplot as plt

def plot_charge_discharge_log_with_dual_axes(log_file):
    """
    ログファイルを解析し、左右の縦軸を使ったSoCと電力の変化をプロットする関数。
    
    Args:
    log_file (str): ログファイルのパス
    """
    timestamps = []
    soc_values = []
    power_values = []
    operation_type = None

    # ログファイルを読み込んでデータを抽出
    with open(log_file, 'r') as f:
        for line in f:
            if "Starting" in line:
                if "Charging" in line:
                    operation_type = "Charging"
                elif "Discharging" in line:
                    operation_type = "Discharging"
            elif "SoC" in line and "Power" in line:
                parts = line.split(" - ")
                timestamp = parts[0].strip("[]")
                soc = float(parts[1].split(", ")[0].split(": ")[1].strip("%"))
                power = int(parts[1].split(", ")[1].split(": ")[1].strip("W"))
                
                timestamps.append(timestamp)
                soc_values.append(soc)
                power_values.append(power)

    # プロットの作成
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 左軸 (SoC)
    ax1.plot(timestamps, soc_values, marker='o', label="SoC (%)", color="blue")
    ax1.set_xlabel("Time")
    ax1.set_ylabel("SoC (%)", color="blue")
    ax1.tick_params(axis='y', labelcolor="blue")
    ax1.set_title(f"{operation_type} Process")

    # 右軸 (電力)
    ax2 = ax1.twinx()  # 同じx軸を共有する
    ax2.plot(timestamps, power_values, marker='o', label="Power (W)", color="red")
    ax2.set_ylabel("Power (W)", color="red")
    ax2.tick_params(axis='y', labelcolor="red")

    # x軸のラベルを回転して見やすくする
    plt.xticks(rotation=45)

    # グラフを表示
    fig.tight_layout()
    plt.show()

# ログファイルを指定してプロット
log_file_path = "charge_discharge_log.txt"
plot_charge_discharge_log_with_dual_axes(log_file_path)
