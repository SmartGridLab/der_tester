import pandas as pd

# CSVファイルを読み込む（例としてファイル名を"data.csv"としています）
file_path = "/workspaces/der_tester/graph_creater/30.csv"
data = pd.read_csv(file_path)

# TargetPower列を計算して追加する関数を定義
def calculate_target_power(row, prev_target_soc):
    if pd.isna(prev_target_soc):
        return 0  # 最初の行では0を返す
    
    # TargetSOCの差分計算
    diff = row['TargetSOC'] - prev_target_soc

    # 充電時と放電時の計算
    if diff > 0:  # 充電
        target_power = (diff / 100) * 4.4 *3600000/1800
    elif diff < 0:  # 放電
        target_power = (diff / 100) * 3.7 *3600000/1800
    else:
        target_power = 0

    return target_power

# 計算用のリストを初期化
target_power_values = []
previous_target_soc = None

# 各行で計算を実施
for index, row in data.iterrows():
    target_power = calculate_target_power(row, previous_target_soc)
    target_power_values.append(target_power)
    previous_target_soc = row['TargetSOC']  # 次の行の計算用に更新

# 新しい列として追加
data['TargetPower'] = target_power_values

# 結果を保存または出力
data.to_csv("/workspaces/der_tester/graph_creater/30.csv", index=False)

print("TargetPower列を追加し、結果をoutput_with_target_power.csvに保存しました。")
