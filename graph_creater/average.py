import pandas as pd

# CSVファイルを読み込む（ファイル名を適宜変更）
data = pd.read_csv(r'/workspaces/der_tester/graph_creater/30.csv')

# TargetSOCとPredictedSOCの差を計算
data['SOC_Difference'] = data['TargetSOC'] - data['PredictedSOC']

# 差の絶対値を計算
data['Absolute_Difference'] = data['SOC_Difference'].abs()

# 0.01以上の差を抽出
greater_than_threshold = data.loc[data['Absolute_Difference'] > 0.01, 'Absolute_Difference']

# 合計と平均を計算
sum_difference = greater_than_threshold.sum()
average_difference = greater_than_threshold.mean()

# 結果を表示
print(f"0.01以上の差の絶対値の合計: {sum_difference}")
print(f"0.01以上の差の絶対値の平均: {average_difference}")
