def bits_to_bytes(b):
    """
    Convert a bit array of length multiple of 8 into a byte array.

    Input:
        b: iterable of bits (each element must be 0 or 1)

    Output:
        bytes object
    """
    b = list(b)

    if len(b) % 8 != 0:
        raise ValueError("Input length must be a multiple of 8.")

    if any(bit not in (0, 1) for bit in b):
        raise ValueError("Input must contain only 0s and 1s.")

    ell = len(b) // 8
    B = [0] * ell

    for i in range(8 * ell):
        B[i // 8] = B[i // 8] + b[i] * (2 ** (i % 8))

    return bytes(B)


def bytes_to_bits(B):
    """
    Convert a byte array into a bit array.
    This is the inverse of bits_to_bytes.

    Input:
        B: bytes-like object or iterable of integers in [0, 255]

    Output:
        list of bits (0 or 1)
    """
    if isinstance(B, bytes):
        B = list(B)
    else:
        B = list(B)

    if any(not (0 <= x <= 255) for x in B):
        raise ValueError("Input must contain only byte values in [0, 255].")

    b = [0] * (8 * len(B))

    for i in range(8 * len(B)):
        b[i] = (B[i // 8] >> (i % 8)) & 1

    return b

def byte_encode(F, d, q=3329):
    """
    Encode an array F of 256 integers into a byte array using d bits per integer.

    Parameters:
        F : iterable of 256 integers
        d : integer, 1 <= d <= 12
        q : modulus used when d == 12 (default: 3329 for ML-KEM)

    Returns:
        bytes object of length 32*d
    """
    F = list(F)

    if len(F) != 256:
        raise ValueError("F must contain exactly 256 integers.")
    if not (1 <= d <= 12):
        raise ValueError("d must satisfy 1 <= d <= 12.")

    m = (1 << d) if d < 12 else q

    for x in F:
        if not (0 <= x < m):
            raise ValueError(f"Each entry of F must be in Z_{m}.")

    b = [0] * (256 * d)

    for i in range(256):
        a = F[i]
        for j in range(d):
            b[i * d + j] = a % 2
            a = (a - b[i * d + j]) // 2

    B = bits_to_bytes(b)
    return B

def byte_decode(B, d, q=3329):
    """
    Decode a byte array B into an array of 256 d-bit integers.

    Parameters:
        B : bytes-like object of length 32*d
        d : integer, 1 <= d <= 12
        q : modulus used when d == 12 (default: 3329 for ML-KEM)

    Returns:
        list of 256 integers
    """
    if not (1 <= d <= 12):
        raise ValueError("d must satisfy 1 <= d <= 12.")

    B = bytes(B)
    if len(B) != 32 * d:
        raise ValueError(f"B must have length {32*d} bytes.")

    m = (1 << d) if d < 12 else q
    b = bytes_to_bits(B)

    F = [0] * 256
    for i in range(256):
        value = 0
        for j in range(d):
            value += b[i * d + j] * (1 << j)
        F[i] = value % m

    return F



def main():
    # bits = [1, 0, 1, 0, 0, 0, 0, 0]   # 00000101 in little-endian bit order
    # print(bits_to_bytes(bits))         # b'\x05'
    # print(list(bits_to_bytes(bits)))   # [5]

    # x = bytes([5])
    # print(bytes_to_bits(x))
    # [1, 0, 1, 0, 0, 0, 0, 0]

    F = [0] * 256
    F[0] = 5
    F[1] = 7
    encoded = byte_encode(F, d=3)
    print(len(encoded))      # 96 = 32 * 3
    print(list(encoded[:4]))


if __name__ == "__main__":
    main()