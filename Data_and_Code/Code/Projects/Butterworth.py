from scipy.signal import butter, filtfilt, sosfilt

def butterworth_filter_default(data, cutoff, fs, order):
    b, a = butter(N=order, Wn=cutoff, btype='low', analog=False, fs=fs)
    y = filtfilt(b, a, data)
    return y
