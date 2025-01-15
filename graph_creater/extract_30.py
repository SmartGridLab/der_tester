import pandas as pd

# CSVファイルを読み込む（ファイル名を適宜変更）
data = pd.read_csv('/workspaces/der_tester/graph_creater/実験データ.csv')

# ElapsedTimeを秒に変換する関数
def time_to_seconds(time_str):
    h, m, s = map(float, time_str.split(':'))
    return int(h * 3600 + m * 60 + s)

# ElapsedTimeを秒に変換した列を追加
data['ElapsedSeconds'] = data['ElapsedTime'].apply(time_to_seconds)

# リセットされる直前の行を抽出
data['TimeDifference'] = data['ElapsedSeconds'].diff().fillna(0)
reset_rows = data[data['TimeDifference'] < 0]
reset_indices = reset_rows.index - 1

# リセット直前の行を取得
result = data.loc[reset_indices].drop(columns=['ElapsedSeconds', 'TimeDifference']).reset_index(drop=True)

# 抽出結果を確認または保存
print(result)
result.to_csv(r'/workspaces/der_tester/graph_creater/30.csv', index=False)
