import os
import subprocess
import json
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
    raise ValueError("API_KEY または SECRET が .env に設定されていません。")

try:
    # 環境変数を設定
    os.environ["uname"] = API_KEY
    os.environ["pass"] = SECRET

    # curlコマンド実行
    curl_command = (
        'curl -X POST "https://trial-hub.iot-exchange.net/v1/token" '
        '-d "grant_type=password&username=$uname&password=$pass"'
    )
    print(f"コマンド実行: {curl_command}")
    result = subprocess.run(curl_command, shell=True, check=True, capture_output=True, text=True)

    # 取得したレスポンスを表示
    response = result.stdout
    print("APIからのレスポンス:")
    print(response)

    # レスポンスからアクセストークンを抽出
    response_json = json.loads(response)
    access_token = response_json.get("access_token")

    if access_token:
        print("アクセストークンを取得しました。")

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
except json.JSONDecodeError as e:
    print(f"レスポンスのJSONデコードに失敗しました: {e}")
