"""
K-PKE is not approved for use in a stand-alone fashion. It serves 
only as a collection of subroutines for use in the algorithms of 
ML-KEM.

While 𝑛 =256 and 𝑞 = 3329 always, the values of the remaining 
parameters 𝑘, 𝜂1, 𝜂2, 𝑑𝑢, and 𝑑𝑣 vary among the three parameter sets.

The algorithms in this section do not perform any input checking because 
they are only invoked as subroutines of the main ML-KEM algorithms. 
The algorithms of ML-KEM themselves do perform input checking as needed.

This description is written in terms of vectors and matrices whose entries 
are elements of 𝑅𝑞. In the actual algorithm, most of the computations 
occur in the NTT domain in order to improve the efficiency of multiplication. 
The relevant vectors and matrices will then have entries in 𝑇𝑞.
"""