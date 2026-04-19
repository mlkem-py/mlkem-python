"""
K-PKE is not approved for use in a stand-alone fashion. It serves 
only as a collection of subroutines for use in the algorithms of 
ML-KEM.

While 𝑛 =256 and 𝑞 = 3329 always, the values of the remaining 
parameters 𝑘, 𝜂1, 𝜂2, 𝑑𝑢, and 𝑑𝑣 vary among the three parameter sets.

The algorithms in this section do not perform any input checking because 
they are only invoked as subroutines of the main ML-KEM algorithms. 
The algorithms of ML-KEM themselves do perform input checking as needed.

This description is written in terms of vectors and matrices whose entries 
are elements of 𝑅𝑞. In the actual algorithm, most of the computations 
occur in the NTT domain in order to improve the efficiency of multiplication. 
The relevant vectors and matrices will then have entries in 𝑇𝑞.
"""
import hash_functions
import ntts
import conversion
import sample

def k_pke_keygen(d, k, eta1, q=3329):
    """
    Implements Algorithm 13: K-PKE.KeyGen(d)

    Assumes the following subroutines are already implemented:

        G(c) -> (rho, sigma)                     # each 32 bytes
        prf(eta, sigma, N) -> bytes             # returns 64*eta bytes
        sample_ntt(B, q=3329) -> list[256]
        sample_poly_cbd(B, eta, q=3329) -> list[256]
        ntt(f, zeta, q=3329) -> list[256]
        multiply_ntts(f_hat, g_hat, zeta, q=3329) -> list[256]
        byte_encode(F, d, q=3329) -> bytes

    Also assumes zeta is the NTT root used by your NTT implementation.
    """
    d = bytes(d)
    if len(d) != 32:
        raise ValueError("d must be exactly 32 bytes.")

    rho, sigma = hash_functions.G(d + bytes([k]))
    N = 0

    # Generate A_hat in (T_q)^{k x k}
    A_hat = [[None for _ in range(k)] for _ in range(k)]
    for i in range(k):
        for j in range(k):
            A_hat[i][j] = sample.sample_ntt(rho + bytes([j, i]), q=q)

    # Generate s in (R_q)^k
    s = [None] * k
    for i in range(k):
        s[i] = sample.sample_poly_cbd(hash_functions.prf(eta1, sigma, N), eta1, q=q)
        N += 1

    # Generate e in (R_q)^k
    e = [None] * k
    for i in range(k):
        e[i] = sample.sample_poly_cbd(hash_functions.prf(eta1, sigma, N), eta1, q=q)
        N += 1

    # NTT(s), NTT(e)
    s_hat = [ntts.ntt(poly, zeta=17, q=q) for poly in s]
    e_hat = [ntts.ntt(poly, zeta=17, q=q) for poly in e]

    # t_hat = A_hat o s_hat + e_hat
    t_hat = []
    for i in range(k):
        acc = [0] * 256
        for j in range(k):
            prod = ntts.multiply_ntts(A_hat[i][j], s_hat[j], zeta=17, q=q)
            acc = [(acc[x] + prod[x]) % q for x in range(256)]
        acc = [(acc[x] + e_hat[i][x]) % q for x in range(256)]
        t_hat.append(acc)

    # ek_PKE = ByteEncode_12(t_hat) || rho
    ek_pke = b"".join(conversion.byte_encode(poly, d=12, q=q) for poly in t_hat) + rho

    # dk_PKE = ByteEncode_12(s_hat)
    dk_pke = b"".join(conversion.byte_encode(poly, d=12, q=q) for poly in s_hat)

    return ek_pke, dk_pke

def main():
    # 32-byte randomness input
    d = bytes(range(32))

    # Example for ML-KEM-512 parameters
    k = 2
    eta1 = 3

    ek_pke, dk_pke = k_pke_keygen(d, k=k, eta1=eta1)

    print("len(ek_pke) =", len(ek_pke))
    print("len(dk_pke) =", len(dk_pke))

    print("ek_pke (first 32 bytes) =", ek_pke[:32].hex())
    print("dk_pke (first 32 bytes) =", dk_pke[:32].hex())


if __name__ == "__main__":
    main()