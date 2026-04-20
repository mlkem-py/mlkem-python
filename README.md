# Python Implementation of ML-KEM Building Blocks

This repository contains a Python implementation of core algorithms from the **Module-Lattice-Based Key-Encapsulation Mechanism (ML-KEM)** standard, standardized by NIST in **FIPS 203**.

The code is intended for **learning, experimentation, and education**. 

## Notes

### 1. This is not a production implementation

This code is **not** intended for deployment in security-critical systems.

### 2. Focus is on algorithm clarity

Some parts are implemented in a straightforward way rather than the most efficient way. For example, the SHAKE128 wrapper uses Python's standard `hashlib` interface and simulates incremental squeezing at the Python level.


## Example

A typical flow for polynomial arithmetic might look like this:

```python
f_hat = ntt(f, zeta=17, q=3329)
g_hat = ntt(g, zeta=17, q=3329)
h_hat = multiply_ntts(f_hat, g_hat, zeta=17, q=3329)
h = ntt_inverse(h_hat, zeta=17, q=3329)
```
```python
k = 2
eta1 = 3
eta2 = 2
du = 10
dv = 4

ek, dk = ml_kem_keygen(k=k, eta1=eta1)
K1, c = ml_kem_encaps(ek, k=k, eta1=eta1, eta2=eta2, du=du, dv=dv)
K2 = ml_kem_decaps(dk, c, k=k, du=du, dv=dv)
```