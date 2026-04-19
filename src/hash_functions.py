import hashlib


def H(s):
    """
    H(s) := SHA3-256(s)

    Input:
        s : bytes-like object

    Output:
        32-byte digest
    """
    s = bytes(s)
    return hashlib.sha3_256(s).digest()


def J(s):
    """
    J(s) := SHAKE256(s, 8 * 32)

    Input:
        s : bytes-like object

    Output:
        32-byte digest
    """
    s = bytes(s)
    return hashlib.shake_256(s).digest(32)


def G(c):
    """
    G(c) := SHA3-512(c)

    Input:
        c : bytes-like object

    Output:
        tuple (a, b), where each is 32 bytes
        and SHA3-512(c) = a || b
    """
    c = bytes(c)
    out = hashlib.sha3_512(c).digest()   # 64 bytes
    a = out[:32]
    b = out[32:]
    return a, b


import hashlib


def prf(eta, s, b):
    """
    PRF_eta(s, b) := SHAKE256(s || b, 8 * 64 * eta)

    Parameters:
        eta : must be 2 or 3
        s   : 32-byte input
        b   : 1-byte input (integer 0..255 or bytes of length 1)

    Returns:
        bytes object of length 64 * eta
    """
    if eta not in (2, 3):
        raise ValueError("eta must be 2 or 3.")

    s = bytes(s)
    if len(s) != 32:
        raise ValueError("s must be exactly 32 bytes.")

    if isinstance(b, int):
        if not (0 <= b <= 255):
            raise ValueError("If b is an integer, it must be in 0..255.")
        b = bytes([b])
    else:
        b = bytes(b)
        if len(b) != 1:
            raise ValueError("b must be exactly 1 byte.")

    return hashlib.shake_256(s + b).digest(64 * eta)

def main():
    # s = b"Hello, World!"

    # print(H(s).hex())
    # print(J(s).hex())

    # a, b = G(s)
    # print(len(a), len(b))  
    # print((a + b).hex())

    s = bytes(range(32))
    out = prf(2, s, 7)

    print(len(out))   # 128
    print(out.hex()[:32])
if __name__ == "__main__":
    main()