import csv
from collections import defaultdict

def extract_soc_bid_data(file_path):
    """
    CSVファイルからSoC_bidデータを抽出し、時間キー（"hour:minute"形式）を使用して辞書に格納する。

    Args:
    file_path (str): CSVファイルのパス

    Returns:
    dict: 各時間キーに対するSoC_bidのリスト
    """
    soc_bid_data = defaultdict(list)
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            hour = row['hour']
            minute = row['minute']
            soc_bid = row['SoC(実需給)']

            # 空データをスキップ
            if not soc_bid:
                continue

            # 時間キーを作成
            time_key = f"{int(hour)}:{int(minute):02d}"

            # SoC_bid値を追加
            soc_bid_data[time_key].append(float(soc_bid))
    
    return dict(soc_bid_data)
