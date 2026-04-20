from mlkem import *

def test_check_encapsulation_input():
    ek, dk = ml_kem_keygen(k=2, eta1=3)
    assert check_encapsulation_input(ek, k=2)

def test_check_decapsulation_input():
    # ML-KEM-512
    k = 2
    eta1 = 3
    eta2 = 2
    du = 10
    dv = 4

    ek, dk = ml_kem_keygen(k=k, eta1=eta1)
    K1, c = ml_kem_encaps(ek, k=k, eta1=eta1, eta2=eta2, du=du, dv=dv)

    assert check_decapsulation_input(dk, c, k, du, dv)

def test_mlkem():
    # ML-KEM-512
    k = 2
    eta1 = 3
    eta2 = 2
    du = 10
    dv = 4

    ek, dk = ml_kem_keygen(k=k, eta1=eta1)
    K1, c = ml_kem_encaps(ek, k=k, eta1=eta1, eta2=eta2, du=du, dv=dv)
    K2 = ml_kem_decaps(dk, c, k=k, du=du, dv=dv)
    
    assert len(K1) == 32  
    assert len(c) == 32 * (du*k + dv) #= 768
    assert K1 == K2

