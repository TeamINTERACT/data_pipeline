'''
Script with article: 
Converting raw accelerometer data to activity counts 
using open source code in Matlab, Python, and R - a comparison to ActiLife activity counts
Corresponding author Ruben Brondeel (ruben.brondeel@umontreal.ca)
This script calculates the Python version of activity counts, 
The functions are a translation of the Matlab function presented in 
Brond JC, Andersen LB, Arvidsson D. Generating ActiGraph Counts from 
Raw Acceleration Recorded by an Alternative Monitor. Med Sci Sports Exerc. 2017.
Python (3.6); run in Eclipse (Oxygen.3a Release (4.7.3a))
'''

import math
import numpy as np
from scipy import signal
import pandas as pd
import resampy

# predefined filter coefficients, as found by Jan Brond
A_coeff = np.array(
    [1, -4.1637, 7.5712, -7.9805, 5.385, -2.4636, 0.89238, 0.06361, -1.3481, 2.4734, -2.9257, 2.9298, -2.7816, 2.4777,
     -1.6847, 0.46483, 0.46565, -0.67312, 0.4162, -0.13832, 0.019852])
B_coeff = np.array(
    [0.049109, -0.12284, 0.14356, -0.11269, 0.053804, -0.02023, 0.0063778, 0.018513, -0.038154, 0.048727, -0.052577,
     0.047847, -0.046015, 0.036283, -0.012977, -0.0046262, 0.012835, -0.0093762, 0.0034485, -0.00080972, -0.00019623])


def pptrunc(data, max_value):
    outd = np.where(data > max_value, max_value, data)
    return np.where(outd < -max_value, -max_value, outd)


def trunc(data, min_value):
    return np.where(data < min_value, 0, data)


def runsum(data, length, threshold):
    N = len(data)
    cnt = int(math.ceil(N / length))

    rs = np.zeros(cnt)

    for n in range(cnt):
        for p in range(length * n, length * (n + 1)):
            if p < N and data[p] >= threshold:
                rs[n] = rs[n] + data[p] - threshold

    return rs


def counts(data, filesf, B=B_coeff, A=A_coeff):
    '''
    Calculate activity counts
    '''
    # define some values obtained from
    deadband = 0.068
    sf = 30
    peakThreshold = 2.13
    adcResolution = 0.0164
    integN = 10
    gain = 0.965

    # since sampling frequency is larger than standard sampling frequency
    # The raw data is resampled to 30hz
    if filesf > sf:
        data = resampy.resample(np.asarray(data), filesf, sf)

    # Butterworth filter in 'scipy' package
    B2, A2 = signal.butter(4, np.array([0.01, 7]) / (sf / 2), btype='bandpass')
    dataf = signal.filtfilt(B2, A2, data)

    # filter in 'scipy' package, based on B and A coefficients described in
    # Brond et al. (2017).
    B = B * gain
    fx8up = signal.lfilter(B, A, dataf)

    # Slicing with step parameter
    fx8 = pptrunc(fx8up[::3], peakThreshold)

    # apply runsum function and return result
    return runsum(np.floor(trunc(np.abs(fx8), deadband) / adcResolution), integN, 0)

