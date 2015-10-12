---
layout: post
title:  "Discrete Fourier Transform"
date:   2015-10-12 11:46:27
---

The latest commit to the project includes my first implementation of the Discrete Fourier transform. This function transforms amplitude-time data to amplitude-frequency data. Essentially, it can be used in spectral analysis to extract all the sinusoids that make up a signal.

It is defined as:

<img src="https://upload.wikimedia.org/math/2/3/9/239d295a8c4ae3619997bfed0a43665c.png"></img>

This formula can be derived further into a form more commonly used in Computer Science:

<img src="https://upload.wikimedia.org/math/f/d/4/fd46b099299d6d80f687f902efb47904.png"></img>

The variables are:

- N = number of time samples we have
- n = current sample we're considering (0...N-1)
- x<sub>n</sub> = value of the signal at time n
- k = current frequency we're considering (0 Hertz up to N-1 Hertz)
- X<sub>k</sub> = amount of frequency k in the signal (Amplitude and Phase, a complex number)

Using this formula, I wrote an implementation in Python. Note that **X** is called **amplitudes** and **k_amp** is the sum of the sequence **x** in my implementation.

{% highlight python %}
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
{% endhighlight %}

The main ambiguity in the definition of the Fourier Transform is the scaling factor of the amplitudes. The many different implementations of the Fourier Transform that can be found on the internet all use different scaling factors. The main three scaling factors that are used are as follows:

- 1 forward, 1/N inverse
- 1/N forward, 1 inverse
- 1/sqrt(N) forward, 1/sqrt(N) inverse

I noticed that Wolfram Alpha was using the 1/sqrt(N) factor. However, I chose to use the factor of 1 for the time being. This is the definition used on Wikipedia.

While this is a good initial implementation, I will be using the Fast Fourier Transform (FFT) in the final project, as it is theoretically around 100 times faster.

I may edit this post a little to explain the Fourier Transform and its implementation better.
