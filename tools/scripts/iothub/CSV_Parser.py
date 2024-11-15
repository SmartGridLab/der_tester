import csv
from collections import defaultdict

def extract_soc_bid_data(file_path):
    """
    CSVファイルからSoC_bidデータを抽出し、時間キー（日、時、30分または00分）を使用して辞書に格納する。
    
    Args:
    file_path (str): CSVファイルのパス

    Returns:
    dict: 各時間キーに対するSoC_bidのリスト
    """
    soc_bid_data = defaultdict(list)
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            day = row['day']
            hour = row['hour']
            minute = row['minute']
            soc_bid = row['SoC_bid[%]']
            
            # Create a key using day, hour, and minute
            time_key = (day, hour, minute)
            
            # Append the SoC_bid value to the list corresponding to the key
            soc_bid_data[time_key].append(float(soc_bid))
    
    return dict(soc_bid_data)
