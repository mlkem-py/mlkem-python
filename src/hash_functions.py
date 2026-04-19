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

def main():
    s = b"Hello, World!"

    print(H(s).hex())
    print(J(s).hex())

    a, b = G(s)
    print(len(a), len(b))  
    print((a + b).hex())


if __name__ == "__main__":
    main()