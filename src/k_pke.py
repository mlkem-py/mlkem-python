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

def k_pke_encrypt(ek_pke, m, r, k, eta1, eta2, du, dv, q=3329):
    """
    Implements Algorithm 14: K-PKE.Encrypt(ek_PKE, m, r)

    Assumes the following subroutines already exist:

        byte_decode(B, d, q=3329)
        byte_encode(F, d, q=3329)
        sample_ntt(B, q=3329)
        sample_poly_cbd(B, eta, q=3329)
        prf(eta, s, b)
        ntt(f, zeta, q=3329)
        ntt_inverse(f_hat, zeta, q=3329)
        multiply_ntts(f_hat, g_hat, zeta, q=3329)
        compress(F, d, q=3329)
        decompress(F, d, q=3329)

    and that your NTT code uses the same zeta value throughout.
    """
    ek_pke = bytes(ek_pke)
    m = bytes(m)
    r = bytes(r)

    if len(m) != 32:
        raise ValueError("m must be exactly 32 bytes.")
    if len(r) != 32:
        raise ValueError("r must be exactly 32 bytes.")
    if len(ek_pke) != 384 * k + 32:
        raise ValueError(f"ek_pke must have length {384*k + 32} bytes.")

    N = 0

    # 1-2: decode t_hat
    t_hat_bytes = ek_pke[:384 * k]
    t_hat = [
        conversion.byte_decode(t_hat_bytes[384 * i:384 * (i + 1)], d=12, q=q)
        for i in range(k)
    ]

    # 3: extract rho
    rho = ek_pke[384 * k:384 * k + 32]

    # 4-8: regenerate A_hat
    A_hat = [[None for _ in range(k)] for _ in range(k)]
    for i in range(k):
        for j in range(k):
            A_hat[i][j] = sample.sample_ntt(rho + bytes([j, i]), q=q)

    # 9-12: generate y
    y = [None] * k
    for i in range(k):
        y[i] = sample.sample_poly_cbd(hash_functions.prf(eta1, r, N), eta1, q=q)
        N += 1

    # 13-16: generate e1
    e1 = [None] * k
    for i in range(k):
        e1[i] = sample.sample_poly_cbd(hash_functions.prf(eta2, r, N), eta2, q=q)
        N += 1

    # 17: generate e2
    e2 = sample.sample_poly_cbd(hash_functions.prf(eta2, r, N), eta2, q=q)

    # 18: y_hat = NTT(y)
    y_hat = [ntts.ntt(poly, zeta=17, q=q) for poly in y]

    # 19: u = NTT^{-1}(A_hat^T o y_hat) + e1
    u = []
    for i in range(k):
        acc = [0] * 256
        for j in range(k):
            # A_hat^T[i,j] = A_hat[j][i]
            prod = ntts.multiply_ntts(A_hat[j][i], y_hat[j], zeta=17, q=q)
            acc = [(acc[x] + prod[x]) % q for x in range(256)]

        poly = ntts.ntt_inverse(acc, zeta=17, q=q)
        poly = [(poly[x] + e1[i][x]) % q for x in range(256)]
        u.append(poly)

    # 20: mu = Decompress_1(ByteDecode_1(m))
    mu = conversion.decompress(conversion.byte_decode(m, d=1, q=q), d=1, q=q)

    # 21: v = NTT^{-1}(t_hat o y_hat) + e2 + mu
    acc = [0] * 256
    for j in range(k):
        prod = ntts.multiply_ntts(t_hat[j], y_hat[j], zeta=17, q=q)
        acc = [(acc[x] + prod[x]) % q for x in range(256)]

    v = ntts.ntt_inverse(acc, zeta=17, q=q)
    v = [(v[x] + e2[x] + mu[x]) % q for x in range(256)]

    # 22: c1 = ByteEncode_du(Compress_du(u))
    c1 = b"".join(conversion.byte_encode(conversion.compress(poly, d=du, q=q), d=du, q=q) for poly in u)

    # 23: c2 = ByteEncode_dv(Compress_dv(v))
    c2 = conversion.byte_encode(conversion.compress(v, d=dv, q=q), d=dv, q=q)

    # 24: c = c1 || c2
    return c1 + c2

def k_pke_decrypt(dk_pke, c, k, du, dv, q=3329):
    """
    Implements Algorithm 15: K-PKE.Decrypt(dk_PKE, c)

    Assumes the following subroutines already exist:

        byte_decode(B, d, q=3329)
        byte_encode(F, d, q=3329)
        decompress(F, d, q=3329)
        compress(F, d, q=3329)
        ntt(f, zeta, q=3329)
        ntt_inverse(f_hat, zeta, q=3329)
        multiply_ntts(f_hat, g_hat, zeta, q=3329)

    Returns:
        m : 32-byte message
    """
    dk_pke = bytes(dk_pke)
    c = bytes(c)

    c1_len = 32 * du * k
    c2_len = 32 * dv

    if len(dk_pke) != 384 * k:
        raise ValueError(f"dk_pke must have length {384 * k} bytes.")
    if len(c) != c1_len + c2_len:
        raise ValueError(f"ciphertext must have length {c1_len + c2_len} bytes.")

    # 1-2: split ciphertext
    c1 = c[:c1_len]
    c2 = c[c1_len:c1_len + c2_len]

    # 3: u' <- Decompress_du(ByteDecode_du(c1))
    u_prime = []
    for i in range(k):
        block = c1[32 * du * i:32 * du * (i + 1)]
        u_prime.append(conversion.decompress(conversion.byte_decode(block, d=du, q=q), d=du, q=q))

    # 4: v' <- Decompress_dv(ByteDecode_dv(c2))
    v_prime = conversion.decompress(conversion.byte_decode(c2, d=dv, q=q), d=dv, q=q)

    # 5: s_hat <- ByteDecode_12(dk_pke)
    s_hat = []
    for i in range(k):
        block = dk_pke[384 * i:384 * (i + 1)]
        s_hat.append(conversion.byte_decode(block, d=12, q=q))

    # 6: w <- v' - NTT^{-1}(s_hat^T o NTT(u'))
    u_hat = [ntts.ntt(poly, zeta=17, q=q) for poly in u_prime]

    acc = [0] * 256
    for i in range(k):
        prod = ntts.multiply_ntts(s_hat[i], u_hat[i], zeta=17, q=q)
        acc = [(acc[j] + prod[j]) % q for j in range(256)]

    temp = ntts.ntt_inverse(acc, zeta=17, q=q)
    w = [(v_prime[j] - temp[j]) % q for j in range(256)]

    # 7: m <- ByteEncode_1(Compress_1(w))
    m = conversion.byte_encode(conversion.compress(w, d=1, q=q), d=1, q=q)

    # 8: return m
    return m

def main():
    # Example parameter set similar to ML-KEM-512
    k = 2
    eta1 = 3
    eta2 = 2
    du = 10
    dv = 4

    d = bytes(range(32))
    ek_pke, dk_pke = k_pke_keygen(d, k=k, eta1=eta1)

    m = bytes([0x42] * 32)
    r = bytes([0x99] * 32)

    c = k_pke_encrypt(ek_pke, m, r, k=k, eta1=eta1, eta2=eta2, du=du, dv=dv)
    print(c[:32].hex())
    m_dec = k_pke_decrypt(dk_pke, c, k=k, du=du, dv=dv)

    print(m_dec == m)

if __name__ == "__main__":
    main()