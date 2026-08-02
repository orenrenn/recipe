def toHiragana(s):
    result = []
    for c in s:
        code = ord(c)
        if 0x30A1 <= code <= 0x30F6 or code == 0x30F4:
            result.append(chr(code - 0x60))
        else:
            result.append(c)
    return ''.join(result)

print(toHiragana("水"))
