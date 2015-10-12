"""
Copyright EJM Software 2015
"""
import math

def dft(x):
    """Computes the discrete Fourier Transform of the 1D array x
    Uses a scaling (normalization) factor of 1"""
    TAU = 6.2831852 # tau is 2 * pi
    N = len(x) # number of samples we have
    amplitudes = [] # amplitudes
    for k in range(0, N): # k is the current frequency being considered
        k_amp = 0 # The amplitude at k is the sum of the following
        for n in range(0, N): # m is the current sample being considered
            theta = TAU*k*n/N
            k_amp += x[n] * (math.cos(theta) + 1j * math.sin(theta))
        amplitudes.append(k_amp)
    return amplitudes

def freqs(n, d):
    """Computes that frequencies that correspond to the dft

    Args:
        n: Sample count
        d: Sample rate

    Returns:
        n length array of integers
    """
    # First half of the list is positive
    frequencies = [(x*d/n) for x in range(0, (n-1)//2 + 1, 1)]
    # Second half of the list is negative
    frequencies += [-(x*d/n) for x in range(n//2, 0, -1)]
    # return
    return frequencies
