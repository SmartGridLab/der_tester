import pandas as pd
import numpy as np

def filter_and_calculate_rmse(file_path):
    # CSVファイルを読み込む
    df = pd.read_csv(file_path)
    
    # TargetSOCの変化率を計算
    df['TargetSOC_Change'] = df['TargetSOC'].diff().abs()
    
    # 変化率が0.1%以上の行をフィルタリング
    filtered_df = df[df['TargetSOC_Change'] > 0.1].copy()
    
    # TargetSOC_Change列を削除（不要な場合）
    filtered_df = filtered_df.drop(columns=['TargetSOC_Change'])
    
    # データが存在しない場合は処理を停止
    if filtered_df.empty:
        print("Filtered data is empty. No RMSE calculation performed.")
        return None
    
    # RMSEを計算 (CurrentSOC と PredictedSOC の差異)
    rmse = np.sqrt(((filtered_df['TargetSOC'] - filtered_df['PredictedSOC']) ** 2).mean())
    
    # 結果を保存する場合（オプション）
    output_file = "filtered_data.csv"
    filtered_df.to_csv(output_file, index=False)
    print(f"Filtered data saved to {output_file}")
    
    return rmse

# 実行例
file_path = "input_data.csv"  # 入力ファイルのパス
rmse = filter_and_calculate_rmse(file_path)
if rmse is not None:
    print(f"RMSE: {rmse}")
