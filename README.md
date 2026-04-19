# Python Implementation of ML-KEM Building Blocks

This repository contains a Python implementation of core algorithms from the **Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)** standard, standardized by NIST in **FIPS 203**.

The code is intended for **learning, experimentation, and reference**. It follows the structure and notation of the standard closely, so the implementation is useful for studying the internal mechanics of ML-KEM and its underlying **K-PKE** construction.

## Scope

This repository currently focuses on the **low-level arithmetic, encoding, sampling, and NTT-related algorithms** used by ML-KEM.

Implemented components include:

- `bits_to_bytes(b)`
- `bytes_to_bits(B)`
- `byte_encode(F, d)`
- `byte_decode(B, d)`
- `sample_poly_cbd(B, eta)`
- `bitrev7(i)`
- `ntt(f, zeta)`
- `ntt_inverse(f_hat, zeta)`
- `base_case_multiply(a0, a1, b0, b1, gamma)`
- `multiply_ntts(f_hat, g_hat, zeta)`
- incremental SHAKE128-style helper functions:
  - `shake128_init()`
  - `shake128_absorb(ctx, data)`
  - `shake128_squeeze(ctx, output_bits)`

These functions correspond to the core utility and polynomial-arithmetic algorithms used inside ML-KEM.

## What ML-KEM Is

ML-KEM is a **post-quantum key-encapsulation mechanism** based on the hardness of the **Module Learning With Errors (MLWE)** problem. At a high level:

1. A public-key encryption scheme is built from MLWE.
2. That scheme is transformed into a CCA-secure KEM using the **Fujisaki-Okamoto transform**.

In practice, ML-KEM is designed for establishing a shared secret over a public channel, which can then be used with symmetric cryptography.

## Design Goals of This Code

The implementation aims to be:

- **Readable**: the code mirrors the pseudocode in the standard as directly as possible
- **Modular**: each algorithm is implemented as a separate Python function
- **Educational**: intermediate algorithmic structure is preserved instead of aggressively optimized
- **Testable**: individual functions can be checked independently

## Important Notes

### 1. This is not a production implementation

This code is **not** intended for deployment in security-critical systems.

It does **not** claim:

- side-channel resistance
- constant-time behavior
- secure memory erasure
- validation for FIPS compliance
- hardened randomness handling

### 2. Focus is on algorithm clarity

Some parts are implemented in a straightforward way rather than the most efficient way. For example, the SHAKE128 wrapper uses Python's standard `hashlib` interface and simulates incremental squeezing at the Python level.

### 3. Parameters

Unless otherwise noted, the implementation assumes the standard ML-KEM modulus:

- `q = 3329`

For NTT-related routines, the caller must provide the appropriate value of `zeta`.

## Overview of Implemented Algorithms

### Bit and Byte Conversion

- **`bits_to_bytes`** converts a bit array into a byte array.
- **`bytes_to_bits`** performs the inverse operation.

These functions use the same bit ordering convention as the standard.

### Encoding and Decoding

- **`byte_encode`** packs 256 integers using `d` bits per coefficient.
- **`byte_decode`** reconstructs the 256 coefficients from the encoded byte array.

These are central to ML-KEM serialization.

### Centered Binomial Sampling

- **`sample_poly_cbd`** samples polynomial coefficients from the centered binomial distribution parameterized by `eta`.

This is used in ML-KEM for generating small secret and error polynomials.

### Bit-Reversal

- **`bitrev7`** computes 7-bit reversal for integers in the range `0..127`.

This is used in the NTT indexing pattern.

### Number-Theoretic Transform

- **`ntt`** computes the forward NTT.
- **`ntt_inverse`** computes the inverse NTT.
- **`base_case_multiply`** multiplies degree-one polynomials modulo `X^2 - gamma`.
- **`multiply_ntts`** multiplies two polynomials in the NTT domain.

These routines are the core of fast polynomial multiplication in ML-KEM.

### SHAKE128 Incremental Wrapper

The repository also includes a lightweight SHAKE128 wrapper with:

- initialization
- absorb
- squeeze

This follows the shape of the incremental API referenced by the standard and is useful for implementing XOF-based routines at a high level.

## Example

A typical flow for polynomial arithmetic might look like this:

```python
f_hat = ntt(f, zeta=17, q=3329)
g_hat = ntt(g, zeta=17, q=3329)
h_hat = multiply_ntts(f_hat, g_hat, zeta=17, q=3329)
h = ntt_inverse(h_hat, zeta=17, q=3329)