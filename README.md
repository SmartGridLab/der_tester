# der_tester
Tester to control various distributed energy resources (DERs) for DER service builders

## How to Use
1. Python のインストール
2. 本ツールで利用するAPIの選択（2023年11月27日現在はIoT-HUBのみ対応）
3. APIアクセスキーの取得（利用するAPIの管理者へお問い合わせください）
4. 本ツールの実行
  - `tools/scripts` から必要なバッチファイルを実行してください 

## 重要な（グラフ作成とかじゃない）実際の操作に関するコード
1. set_and_get.py　→　最も基本的なコード　これが出来たらコマンドを装置に送信することができる
2. kensyou.py　→　複数のコマンドをテストしたい、連続的にテストしたい場合に使用するコード

## ここからは計画通りに動かすためのコード
3. Battery.py →　充放電、停止をメソッド化し、呼びやすくするコード　
4. main.py →　実際にメソッドを呼び出して使って、蓄電池を計画通りに制御し、ログを作成するコード
5. characteristics.py →　装置を0~100で充放電し、特性を確認するコード

## 参考文献や動作マニュアル
[Google Drive](https://drive.google.com/drive/folders/196UOfYqHFDTonQh8NCdOVm2RNF1meveH?usp=sharing)に集積していきます。  
欲しい論文があれば、slackの **# 欲しい論文リクエスト** で荒井さんにリクエストしてください。暇があれば小平も渡します。  

[強化学習とのI/Fの図](https://boardmix.com/app/share/CAE.CNX6ICAFKhZLQnc3cUZVU0ctYkJUUU9CVGJJWDBnMAVAAQ，リンクをクリックして、Boardmix)
