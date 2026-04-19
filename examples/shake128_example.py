from shake import *

def shake128_example(strs, block_lengths):
    """
    Perform a sequence of SHAKE128 absorb operations followed by
    a sequence of squeeze operations.

    Parameters:
        strs          : iterable of byte arrays [str1, ..., str_m]
        block_lengths : iterable of positive integers [b1, ..., b_l],
                        where each b_j is the number of output bytes to squeeze

    Returns:
        bytes object of length sum(block_lengths)
    """
    ctx = shake128_init()

    for s in strs:
        ctx = shake128_absorb(ctx, s)

    output_parts = []
    for b in block_lengths:
        if b <= 0:
            raise ValueError("Each output length must be a positive integer.")
        ctx, out_j = shake128_squeeze(ctx, 8 * b)
        output_parts.append(out_j)

    return b"".join(output_parts)


def main():
    out = shake128_example(
    [b"abc", b"def"],
    [4, 6, 3]
    )

    print(out)
    print(len(out))   # 13

if __name__ == "__main__":
    main()