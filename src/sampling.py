from src.conversion import *

def sample_poly_cbd(B, eta, q=3329):
    """
    Sample a polynomial f from the centered binomial distribution D_eta(R_q).

    Parameters:
        B   : bytes-like object of length 64 * eta
        eta : integer parameter (typically 2 or 3 in ML-KEM contexts)
        q   : modulus (default: 3329)

    Returns:
        list of 256 integers in Z_q
    """
    B = bytes(B)
    if eta <= 0:
        raise ValueError("eta must be positive.")
    if len(B) != 64 * eta:
        raise ValueError(f"B must have length {64 * eta} bytes.")

    b = bytes_to_bits(B)
    f = [0] * 256

    for i in range(256):
        x = 0
        y = 0

        for j in range(eta):
            x += b[2 * i * eta + j]
            y += b[2 * i * eta + eta + j]

        f[i] = (x - y) % q

    return f

def main():
    B = bytes([37] * (64 * 2))   # eta = 2
    f = sample_poly_cbd(B, eta=2)
    print(len(f))   # 256
    print(f)    # 

main()