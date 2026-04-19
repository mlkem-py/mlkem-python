import ntts

def test_ntt():
    f = [0] * 256
    f_hat = ntts.ntt(f)
    assert f_hat[:8] == [0]*8
