import os
import subprocess
from dotenv import load_dotenv, set_key

# スクリプトのあるディレクトリを取得
current_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(current_dir, ".env")

# .envファイルをロード
load_dotenv(dotenv_path=env_file_path)

# 環境変数を取得
API_KEY = os.getenv("API_KEY")
SECRET = os.getenv("SECRET")

# エラーチェック
if not API_KEY or not SECRET:
    raise ValueError("API_KEYまたはSECRETが.envに設定されていません。")

try:
    # 1. export uname=[API_KEY]
    export_uname_command = f"export uname={API_KEY}"
    subprocess.run(export_uname_command, shell=True, check=True, executable="/bin/bash")
    print(f"コマンド実行: {export_uname_command}")

    # 2. export pass=[SECRET]
    export_pass_command = f"export pass={SECRET}"
    subprocess.run(export_pass_command, shell=True, check=True, executable="/bin/bash")
    print(f"コマンド実行: {export_pass_command}")

    # 3. curlコマンドを実行
    curl_command = (
        'curl -X POST "https://trial-hub.iot-exchange.net/v1/token" '
        '-d "grant_type=password&username=$uname&password=$pass"'
    )
    result = subprocess.run(curl_command, shell=True, check=True, capture_output=True, text=True, executable="/bin/bash")
    print(f"コマンド実行: {curl_command}")

    # 取得した結果を表示
    response = result.stdout
    print("APIからのレスポンス:")
    print(response)

    # レスポンスからアクセストークンを抽出（JSONフォーマット想定）
    import json
    response_json = json.loads(response)
    access_token = response_json.get("access_token")

    if access_token:
        # .envファイルの既存のACCESS_TOKENを削除
        with open(env_file_path, "r") as file:
            lines = file.readlines()
        
        with open(env_file_path, "w") as file:
            for line in lines:
                if not line.startswith("ACCESS_TOKEN="):
                    file.write(line)
        
        # 新しいACCESS_TOKENを.envに保存
        set_key(env_file_path, "ACCESS_TOKEN", access_token)
        print(".envファイルに新しいアクセストークンを保存しました。")
    else:
        print("レスポンスにアクセストークンが含まれていません。")

except subprocess.CalledProcessError as e:
    print(f"コマンド実行中にエラーが発生しました: {e}")
