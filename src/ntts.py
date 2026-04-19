def bitrev7(i):
    """
    Return BitRev_7(i), the integer obtained by reversing
    the 7-bit binary representation of i.

    Requires: 0 <= i <= 127
    """
    if not (0 <= i <= 127):
        raise ValueError("i must satisfy 0 <= i <= 127")

    result = 0
    for _ in range(7):
        result = (result << 1) | (i & 1)
        i >>= 1

    return result

def ntt(f, zeta = 17, q=3329):
    """
    Compute the NTT of f according to Algorithm 9.

    Parameters:
        f    : iterable of 256 integers in Z_q
        zeta : an element of Z_q used in the powers zeta^BitRev7(i), primitive 256-th root of unity modulo 𝑞
        q    : modulus (default: 3329)

    Returns:
        list of 256 integers representing the NTT of f
    """
    f_hat = list(f)

    if len(f_hat) != 256:
        raise ValueError("f must contain exactly 256 coefficients.")
    if any(not (0 <= x < q) for x in f_hat):
        raise ValueError("All coefficients of f must be in Z_q.")

    i = 1
    length = 128

    while length >= 2:
        start = 0
        while start < 256:
            zeta_i = pow(zeta, bitrev7(i), q)
            i += 1

            for j in range(start, start + length):
                t = (zeta_i * f_hat[j + length]) % q
                f_hat[j + length] = (f_hat[j] - t) % q
                f_hat[j] = (f_hat[j] + t) % q

            start += 2 * length

        length //= 2

    return f_hat

def ntt_inverse(f_hat, zeta = 17, q=3329):
    """
    Compute the inverse NTT according to Algorithm 10.

    Parameters:
        f_hat : iterable of 256 integers in Z_q
        zeta  : an element of Z_q used in the powers zeta^BitRev7(i)
        q     : modulus (default: 3329)

    Returns:
        list of 256 integers representing the inverse NTT
    """
    f = list(f_hat)

    if len(f) != 256:
        raise ValueError("f_hat must contain exactly 256 coefficients.")
    if any(not (0 <= x < q) for x in f):
        raise ValueError("All coefficients of f_hat must be in Z_q.")

    i = 127
    length = 2

    while length <= 128:
        start = 0
        while start < 256:
            zeta_i = pow(zeta, bitrev7(i), q)
            i -= 1

            for j in range(start, start + length):
                t = f[j]
                f[j] = (t + f[j + length]) % q
                f[j + length] = (zeta_i * (f[j + length] - t)) % q

            start += 2 * length

        length *= 2

    for j in range(256):
        f[j] = (f[j] * 3303) % q   # 3303 == 128^{-1} mod 3329

    return f

def base_case_multiply(a0, a1, b0, b1, gamma, q=3329):
    """
    Compute the product of two degree-one polynomials
    (a0 + a1*X) and (b0 + b1*X) modulo X^2 - gamma over Z_q.

    Returns:
        (c0, c1) where
        c0 = a0*b0 + a1*b1*gamma mod q
        c1 = a0*b1 + a1*b0 mod q
    """
    for x in (a0, a1, b0, b1, gamma):
        if not (0 <= x < q):
            raise ValueError("All inputs must be in Z_q.")

    c0 = (a0 * b0 + a1 * b1 * gamma) % q
    c1 = (a0 * b1 + a1 * b0) % q

    return c0, c1

def multiply_ntts(f_hat, g_hat, zeta=17, q=3329):
    """
    Compute the product of two NTT representations according to Algorithm 11.

    Parameters:
        f_hat : iterable of 256 integers in Z_q
        g_hat : iterable of 256 integers in Z_q
        zeta  : element of Z_q
        q     : modulus (default: 3329)

    Returns:
        h_hat : list of 256 integers in Z_q
    """
    f_hat = list(f_hat)
    g_hat = list(g_hat)

    if len(f_hat) != 256 or len(g_hat) != 256:
        raise ValueError("f_hat and g_hat must each contain exactly 256 coefficients.")
    if any(not (0 <= x < q) for x in f_hat):
        raise ValueError("All coefficients of f_hat must be in Z_q.")
    if any(not (0 <= x < q) for x in g_hat):
        raise ValueError("All coefficients of g_hat must be in Z_q.")

    h_hat = [0] * 256

    for i in range(128):
        gamma = pow(zeta, 2 * bitrev7(i) + 1, q)
        h_hat[2 * i], h_hat[2 * i + 1] = base_case_multiply(
            f_hat[2 * i],
            f_hat[2 * i + 1],
            g_hat[2 * i],
            g_hat[2 * i + 1],
            gamma,
            q
        )

    return h_hat

def main():
    # f = [15] * 256
    
    # f_hat = ntt(f)
    # print(f_hat[:8])

    # out = ntt_inverse(f_hat, zeta=17, q=3329)
    # print(len(out))      # 256
    # print(out[:8])

    f_hat = [0] * 256
    g_hat = [23] * 256
    f_hat[0] = 12
    g_hat[5] = 100

    h_hat = multiply_ntts(f_hat, g_hat, zeta=17, q=3329)
    print(h_hat[:8])


if __name__ == "__main__":
    main()