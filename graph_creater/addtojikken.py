import pandas as pd

# 元のCSVファイルと宛先CSVファイルのパス
source_file_path = "/workspaces/der_tester/graph_creater/30.csv"
destination_file_path = "/workspaces/der_tester/graph_creater/実験データ.csv"

# CSVファイルを読み込む
source_data = pd.read_csv(source_file_path)
destination_data = pd.read_csv(destination_file_path)

# TargetPower列を追加するリスト
mapped_target_power = []

# 元データのインデックスを初期化
source_index = 0

# 宛先データのElapsedTimeが減少したら、元データの次の行に切り替える
for i, row in destination_data.iterrows():
    if i > 0 and destination_data.loc[i, 'ElapsedTime'] < destination_data.loc[i - 1, 'ElapsedTime']:
        source_index = min(source_index + 1, len(source_data) - 1)  # 次の行に切り替え
    
    # 元データからTargetPowerを取得して追加
    mapped_target_power.append(source_data.loc[source_index, 'TargetPower'])

# 新しい列を宛先データに追加
destination_data['TargetPower'] = mapped_target_power

# 結果を保存
destination_data.to_csv("output_with_mapped_target_power.csv", index=False)

print("TargetPower列を追加し、結果をoutput_with_mapped_target_power.csvに保存しました。")
