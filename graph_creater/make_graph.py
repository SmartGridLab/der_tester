import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import font_manager

# 日本語フォントを明示的に指定
font_path = r"/workspaces/der_tester/graph_creater/MSGOTHIC.TTC"  # WindowsのMSゴシックフォントパス
# font_path = "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"  # LinuxのNoto Sansフォントパス
# font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"  # macOSのヒラギノフォントパス

font_prop = font_manager.FontProperties(fname=font_path)
rcParams['font.family'] = font_prop.get_name()
rcParams['axes.unicode_minus'] = False  # マイナス記号を正しく表示

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
    target_powers = []

    with open(csv_file_path, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        prev_seconds = 0
        cumulative_offset = 0
        for i, row in enumerate(reader):
            elapsed_str = row['ElapsedTime']
            current_soc = float(row['CurrentSOC'])
            target_soc = float(row['TargetSOC'])
            predicted_soc = float(row['PredictedSOC'])
            power = float(row['Power'])
            target_power = float(row.get('TargetPower', 0))

            current_seconds = parse_elapsed_time_to_seconds(elapsed_str)

            if i > 0 and current_seconds < prev_seconds:
                cumulative_offset += prev_seconds

            cumulative_time = current_seconds + cumulative_offset

            times.append(cumulative_time)
            target_socs.append(target_soc)
            predicted_socs.append(predicted_soc)
            correct_socs.append(current_soc)
            powers.append(power)
            target_powers.append(target_power)

            prev_seconds = current_seconds

    title_fontsize = 25
    label_fontsize = 20
    tick_fontsize = 20
    line_width = 4

    fig1 = plt.figure(figsize=(10, 6))
    ax1 = fig1.add_subplot(111)
    ax1.plot(times, target_socs, color='red', label='目標SOC値', linewidth=line_width)
    ax1.plot(times, predicted_socs, color='blue', label='予測SOC値', linewidth=line_width)
    ax1.plot(times, correct_socs, color='green', label='確定SOC値', linewidth=line_width)
    ax1.set_ylabel('SOC (%)', fontsize=label_fontsize)
    ax1.set_xlabel('経過時間 (秒)', fontsize=label_fontsize)
    ax1.set_ylim(0, 110)
    ax1.set_title('SOCの推移', fontsize=title_fontsize)
    ax1.tick_params(axis='both', which='major', labelsize=tick_fontsize)
    ax1.legend(fontsize=tick_fontsize)
    ax1.grid(True)
    plt.tight_layout()

    fig2 = plt.figure(figsize=(10, 6))
    ax2 = fig2.add_subplot(111)
    ax2.plot(times, powers, color='purple', label='瞬時充放電電力 (W)', linewidth=line_width)
    ax2.plot(times, target_powers, color='orange', linestyle='--', label='目標瞬時充放電電力 (W)', linewidth=line_width)
    ax2.set_ylabel('瞬時充放電電力 (W)', fontsize=label_fontsize)
    ax2.set_xlabel('経過時間 (秒)', fontsize=label_fontsize)
    ax2.set_ylim(-1400, 1400)
    ax2.set_title('電力の推移', fontsize=title_fontsize)
    ax2.tick_params(axis='both', which='major', labelsize=tick_fontsize)
    ax2.legend(fontsize=tick_fontsize)
    ax2.grid(True)
    plt.tight_layout()

    plt.show()

if __name__ == "__main__":
    csv_file_path = r"/workspaces/der_tester/output_with_mapped_target_power.csv"
    plot_graphs(csv_file_path)
