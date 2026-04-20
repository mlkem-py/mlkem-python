"""
7. The ML-KEM Key-Encapsulation Mechanism
To instantiate ML-KEM, one must select a parameter set:
ML-KEM-512, ML-KEM-768, and ML-KEM-1024
Each parameter set assigns specific numerical values to the 
individual parameters 𝑛, 𝑞, 𝑘, 𝜂1, 𝜂2, 𝑑𝑢, and 𝑑𝑣. While 𝑛 is 
always 256 and 𝑞 is always 3329, the remaining parameters vary 
among the three parameter sets

"""
import secrets
import mlkem_internal
import conversion
import hash_functions

def ml_kem_keygen(k, eta1):
    """
    Implements Algorithm 19: ML-KEM.KeyGen()

    Parameters:
        k    : parameter set value
        eta1 : parameter set value

    Returns:
        (ek, dk)

    Raises:
        RuntimeError if randomness generation fails.
    """
    try:
        d = secrets.token_bytes(32)
        z = secrets.token_bytes(32)
    except Exception as e:
        raise RuntimeError("Random byte generation failed.") from e

    if d is None or z is None:
        raise RuntimeError("Random byte generation failed.")

    ek, dk = mlkem_internal.keygen_internal(d, z, k=k, eta1=eta1)
    return ek, dk

def ml_kem_encaps(ek, k, eta1, eta2, du, dv):
    """
    Implements Algorithm 20: ML-KEM.Encaps(ek)

    Parameters:
        ek   : checked encapsulation key
        k    : parameter set value
        eta1 : parameter set value
        eta2 : parameter set value
        du   : compression parameter
        dv   : compression parameter

    Returns:
        (K, c)

    Raises:
        RuntimeError if randomness generation fails.
    """

    ek = bytes(ek)

    try:
        m = secrets.token_bytes(32)
    except Exception as e:
        raise RuntimeError("Random byte generation failed.") from e

    if m is None:
        raise RuntimeError("Random byte generation failed.")

    K, c = mlkem_internal.encaps_internal(ek, m, k=k, eta1=eta1, eta2=eta2, du=du, dv=dv)
    return K, c


def ml_kem_decaps(dk, c, k, du, dv):
    """
    Implements Algorithm 21: ML-KEM.Decaps(dk, c)

    Parameters:
        dk : checked decapsulation key
        c  : checked ciphertext
        k  : parameter set value
        du : compression parameter
        dv : compression parameter

    Returns:
        K : 32-byte shared secret key
    """
    return mlkem_internal.decaps_internal(dk, c, k=k, du=du, dv=dv)


def check_encapsulation_input(ek, k, q=3329):
    """
    Check whether ek is a valid candidate encapsulation key.

    Returns:
        True  if the check passes
        False if the check fails
    """
    # 1. Type/length check
    if not isinstance(ek, (bytes, bytearray)):
        return False

    ek = bytes(ek)
    expected_len = 384 * k + 32
    if len(ek) != expected_len:
        return False

    # 2. Modulus check
    prefix = ek[:384 * k]
    test = b"".join(
        conversion.byte_encode(
            conversion.byte_decode(prefix[384 * i:384 * (i + 1)], d=12, q=q),
            d=12,
            q=q
        )
        for i in range(k)
    )

    if test != prefix:
        return False

    return True

def check_decapsulation_input(dk, c, k, du, dv):
    """
    Check whether dk and c satisfy the decapsulation input checks.

    Returns:
        True  if all checks pass
        False otherwise
    """
    # 1. Ciphertext type/length check
    if not isinstance(c, (bytes, bytearray)):
        return False
    c = bytes(c)
    if len(c) != 32 * (du * k + dv):
        return False

    # 2. Decapsulation key type/length check
    if not isinstance(dk, (bytes, bytearray)):
        return False
    dk = bytes(dk)
    if len(dk) != 768 * k + 96:
        return False

    # 3. Hash check
    ek = dk[384 * k : 768 * k + 32]
    stored_h = dk[768 * k + 32 : 768 * k + 64]
    test = hash_functions.H(ek)

    if test != stored_h:
        return False

    return True

def main():
    # ML-KEM-512
    k = 2
    eta1 = 3
    eta2 = 2
    du = 10
    dv = 4

    ek, dk = ml_kem_keygen(k=k, eta1=eta1)
    K1, c = ml_kem_encaps(ek, k=k, eta1=eta1, eta2=eta2, du=du, dv=dv)
    K2 = ml_kem_decaps(dk, c, k=k, du=du, dv=dv)
    
    print(len(K1))   # 32
    print(len(c))   # 32 * (du*k + dv) = 768
    print(len(K2))   # 32
    print(K1 == K2)
    print(check_decapsulation_input(dk, c, k, du, dv)) 
if __name__ == "__main__":
    main()