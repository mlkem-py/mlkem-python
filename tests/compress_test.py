from conversion import compress, decompress

def test_compress():
    c = 5
    d = 4
    assert compress(decompress(c,d), d) == c