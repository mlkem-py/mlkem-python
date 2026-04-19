"""
NIST Special Publication 800-185 - Section 3 (cShake)
FIPS 203 Module-Lattice-Based Key-Encapsulation Mechanism Standard
"""
import hashlib

class SHAKE128Context:
    """
    Simple context wrapper for an incremental SHAKE128-style API.

    This is not a low-level mutable sponge state. Instead, it stores:
      - absorbed input bytes
      - current squeeze position (in bytes)

    Squeeze(ctx, 8*z) returns the next z output bytes and advances the context.
    """

    def __init__(self):
        self.absorbed = b""
        self.squeeze_pos = 0


def shake128_init():
    """
    ctx <- SHAKE128.Init()

    Initialize a SHAKE128 context.
    """
    return SHAKE128Context()


def shake128_absorb(ctx, data):
    """
    ctx <- SHAKE128.Absorb(ctx, data)

    Absorb bytes into the context.

    Parameters:
        ctx  : SHAKE128Context
        data : bytes-like object

    Returns:
        updated ctx
    """
    if not isinstance(ctx, SHAKE128Context):
        raise TypeError("ctx must be a SHAKE128Context")

    data = bytes(data)
    ctx.absorbed += data
    return ctx


def shake128_squeeze(ctx, output_bits):
    """
    (ctx, B) <- SHAKE128.Squeeze(ctx, output_bits)

    Extract output_bits bits from the squeezing phase and update the context.

    This implementation supports only output lengths that are multiples of 8,
    so the output is always a byte array.

    Parameters:
        ctx         : SHAKE128Context
        output_bits : requested output length in bits

    Returns:
        (ctx, B) where B is a bytes object
    """
    if not isinstance(ctx, SHAKE128Context):
        raise TypeError("ctx must be a SHAKE128Context")
    if output_bits % 8 != 0:
        raise ValueError("output_bits must be a multiple of 8")

    z = output_bits // 8
    total_needed = ctx.squeeze_pos + z

    # Compute enough SHAKE128 output, then return the next chunk.
    full_output = hashlib.shake_128(ctx.absorbed).digest(total_needed)
    B = full_output[ctx.squeeze_pos:total_needed]
    ctx.squeeze_pos = total_needed

    return ctx, B


def main():
    ctx = shake128_init()
    ctx = shake128_absorb(ctx, b"abc")

    ctx, out1 = shake128_squeeze(ctx, 16)   # 2 bytes
    ctx, out2 = shake128_squeeze(ctx, 24)   # next 3 bytes

    print(out1)
    print(out2)
    print(out1 + out2 == hashlib.shake_128(b"abc").digest(5))  # True


if __name__ == "__main__":
    main()