"""
The incremental API for SHAKE128 will only be invoked through a wrapper XOF.
XOF follows the convention that all wrapper functions treat 
inputs and outputs as byte arrays and measure the lengths of all such arrays 
in terms of bytes.
"""
import shake
def init():
    return shake.shake128_init()
def absorb(ctx, string):
    return shake.shake128_absorb(ctx, string)
def squeeze(ctx, ell):
    return shake.shake128_squeeze(ctx, 8*ell)