import hashlib
from shake import *

def test_shake():
    ctx = shake128_init()
    ctx = shake128_absorb(ctx, b"abc")

    ctx, out1 = shake128_squeeze(ctx, 16)   # 2 bytes
    ctx, out2 = shake128_squeeze(ctx, 24)   # next 3 bytes
    
    assert out1 + out2 == hashlib.shake_128(b"abc").digest(5)