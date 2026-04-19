"""
The algorithms of ML-KEM require two sampling subroutines: 
sample_ntt and sample_poly_cbd
Both of these algorithms can be used to convert a stream of uniformly 
random bytes into a sample from some desired distribution. 
These algorithms will be invoked with a stream of pseudorandom bytes 
as the input. The output will then be a sample from a distribution 
that is computationally indistinguishable from the desired distribution.
"""

import xof
import conversion

def sample_ntt(B, q=3329):
    """
    Sample an element of T_q using Algorithm 7.

    Input:
        B : bytes-like object of length 34
            (32-byte seed + 2 index bytes)

    Output:
        list a_hat of 256 integers in Z_q
    """
    B = bytes(B)
    if len(B) != 34:
        raise ValueError("B must be exactly 34 bytes.")

    ctx = xof.init()
    ctx = xof.absorb(ctx, B)

    a_hat = [0] * 256
    j = 0

    while j < 256:
        ctx, C = xof.squeeze(ctx, 3)   # C is 3 bytes

        d1 = C[0] + 256 * (C[1] % 16)
        d2 = (C[1] // 16) + 16 * C[2]

        if d1 < q:
            a_hat[j] = d1
            j += 1

        if d2 < q and j < 256:
            a_hat[j] = d2
            j += 1

    return a_hat

def sample_poly_cbd(B, eta, q=3329):
    """
    Implements SamplePolyCBD_eta(B).

    Parameters:
        B   : bytes-like object of length 64 * eta
        eta : positive integer
        q   : modulus (default: 3329)

    Returns:
        list f of 256 integers in Z_q
    """
    B = bytes(B)
    if eta <= 0:
        raise ValueError("eta must be positive.")
    if len(B) != 64 * eta:
        raise ValueError(f"B must have length {64 * eta} bytes.")

    b = conversion.bytes_to_bits(B)
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
    seed_and_indices = bytes(range(34))
    a_hat = sample_ntt(seed_and_indices)

    print(len(a_hat))     # 256
    print(a_hat[:10])

    B = bytes([1] * (64 * 2))
    f = sample_poly_cbd(B, eta=2)

    print(len(f))   # 256
    print(f[:8])

if __name__ == "__main__":
    main()