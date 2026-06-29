t_bytes = (
        "00000000000100101000001010010011",
        "00000000000100101000001010010011",
        "00000000000100101000001010010011",
        "00000000000100101000001010010011",
        "00000000000100101000001010010011")

lenght = len(t_bytes) * 4 + 4
with open("output2.bin", "wb") as f:
    f.write(lenght.to_bytes(4, byteorder="little"))
    for byte in t_bytes:
        b = int(byte, 2).to_bytes(len(byte) // 8, byteorder="little")
        f.write(b)