def twos_complement_to_int(bit_str):
    if len(bit_str) != 32:
        raise ValueError("入力は32ビットの文字列でなければなりません。")
    # まずは符号なし整数として変換
    value = int(bit_str, 2)
    # 符号ビットが1の場合は、2^32を引くことで負の値に変換
    if bit_str[0] == '1':
        value -= 2**32
    return value

# 例: 1200の32ビット2の補数表現から整数に変換
bit_str = format(1200, '032b')
print("ビット列:", bit_str)
number = twos_complement_to_int(bit_str)
print("変換された整数:", number)
