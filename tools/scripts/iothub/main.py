#充放電メソッド、PoCチェックメソッドを呼び出し、値を上（強化学習のやつ）に返すコード
#引数：まだわからない。csvを処理した結果？
#戻り値：
#PoCチェックの時：check_POC_method.run_check_POC_method()の戻り値(辞書型のres1または"ERROR"）を返す。
#放電指令の時：充電から放電の成功:CD01,停止から放電の成功:SD01,既に放電中：DD01,失敗:ERROR
#充電指令の時：放電から充電の成功:DC01,停止から充電の成功:SC01,既に充電中：CC01,失敗:ERROR
import charging_method
import discharging_method
import check_POC_method
import datetime
import requests
import json
import os
from dotenv import load_dotenv
import time
import sys

#charging_method.run_charging_method()
#discharging_method.run_discharging_method()
check_POC_method.run_check_POC_method()
