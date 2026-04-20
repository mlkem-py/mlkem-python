from mlkem_internal import *

def test_mlkem_internal():
    d = bytes(range(32))
    z = bytes(range(32, 64))

    # Example: ML-KEM-512 parameters
    k = 2
    du = 10
    dv = 4

    d = bytes(range(32))
    z = bytes(range(32, 64))
    m = bytes([7] * 32)

    ek, dk = keygen_internal(d, z, k=k, eta1=ETA1)
    K1, c = encaps_internal(ek, m, k=k, eta1=ETA1, eta2=ETA2, du=du, dv=dv)
    K2 = decaps_internal(dk, c, k=k, du=du, dv=dv)
    assert K1 == K2