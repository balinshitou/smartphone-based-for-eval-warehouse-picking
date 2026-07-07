import numpy as np
import pywt

def waveletDenoise(time, acceleration):
    coeffs = pywt.wavedec(acceleration, 'db4', level=3)
    # threshold processing
    threshold = np.median(np.abs(coeffs[-1])) / 0.6745
    new_coeffs = list(map(lambda x: pywt.threshold(x, value=threshold, mode='soft'), coeffs))
    # inverse wavelet transform
    denoised_signal = pywt.waverec(new_coeffs, 'db4')
    return denoised_signal[:len(time)]