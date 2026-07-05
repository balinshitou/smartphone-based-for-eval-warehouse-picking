import math
import numpy as np
import matplotlib.pyplot as plt


def detrend_signal(signal):
    time = np.arange(len(signal))
    slope, intercept = np.polyfit(time, signal, 1)
    detrended_signal = signal - (slope * time + intercept)
    return detrended_signal
    # return signal


def local_maxima_scalogram(detrended_signal, L):
    N = len(detrended_signal)

    M = np.zeros((L, N))
    for k in range(1, L + 1):
        for i in range(k + 2, N - k + 2):
            # if i < N:
            if detrended_signal[i - 1 - 1] > detrended_signal[i - k - 1 - 1] and detrended_signal[i - 1 - 1] > \
                    detrended_signal[i + k - 1 - 1]:
                M[k - 1, i - 1] = 0
            else:
                # M[k - 1, i - 1] = random.random() + 1
                M[k - 1, i - 1] = np.random.uniform(0, 1) + 1
        # 边界计算
        for i in range(1, k + 2):
            if i < N:
                M[k - 1, i - 1] = np.random.uniform(0, 1) + 1
        for i in range(N - k + 2, N + 1):
            if i <= N:
                M[k - 1, i - 1] = np.random.uniform(0, 1) + 1
    return M


def row_summation(M):
    return M.sum(axis=1)


def max_zero(M):
    zeros_count = []
    for row in range(len(M)):
        count = 0
        for item in M[row]:
            if item == 0:
                count += 1
        zeros_count.append(count)
    max_value = max(zeros_count)
    max_index = zeros_count.index(max_value)
    argmin = max_index + 1
    return argmin


def find_optimal_scale(gamma):
    argmin = np.argmin(gamma) + 1
    return argmin


def reshape_matrix(M, lambda_scale):
    return M[:lambda_scale, :]


def detect_peaks(Mr):
    if Mr.shape[0] == 1:
        std_dev = Mr[0]
        zero_std_indices = np.where(Mr[0] == 0)[0]
    else:
        std_dev = Mr.std(axis=0, ddof=1)
        zero_std_indices = np.where(std_dev == 0)[0]

    return zero_std_indices, std_dev


def visualize_signal(signal, detrended_signal, M, Mr, peaks_indices, std_dev):
    plt.figure(figsize=(18, 8))

    plt.subplot(2, 3, 1)
    plt.plot(signal, color='yellow', label='Original Signal')
    plt.plot(detrended_signal, color='green', label='Detrended Signal')
    plt.title('Original Signal and Detrended Signal')
    plt.xlabel('Sample Index')
    plt.ylabel('Amplitude')

    plt.subplot(2, 3, 2)
    plt.imshow(M, aspect='auto', cmap='hot', interpolation='nearest')
    plt.title('Local Maxima Scalogram (LMS)')
    plt.xlabel('Time')
    plt.ylabel('Scale')
    plt.colorbar(label='Value')

    # LMS
    plt.subplot(2, 3, 3)
    plt.imshow(Mr, aspect='auto', cmap='hot', interpolation='nearest')
    plt.title('Local Maxima Scalogram (LMS) Mr')
    plt.xlabel('Time')
    plt.ylabel('Scale')
    plt.colorbar(label='Value')

    plt.subplot(2, 3, 5)
    plt.plot(std_dev)
    plt.title('Local Maxima Scalogram (LMS) Mr-Deviation')
    plt.xlabel('Time')
    plt.ylabel('Deviation')
    # plt.colorbar(label='Value')

    plt.subplot(2, 3, 6)
    plt.plot(detrended_signal)
    plt.title('Summed LMS and Detected Peaks')
    plt.xlabel('Sample Index')
    plt.ylabel('Summed Value')
    peaks_indices -= 1
    plt.scatter(peaks_indices, detrended_signal[peaks_indices], color='red')

    plt.tight_layout()
    plt.show()


def ampd_algorithm(data):
    signal = data
    detrended_signal = detrend_signal(signal)
    L = math.ceil(len(signal) / 2) - 1
    M = local_maxima_scalogram(detrended_signal, L)
    lambda_scale = max_zero(M)
    Mr = reshape_matrix(M, lambda_scale)
    peaks_indices, std_dev = detect_peaks(Mr)
    return signal, detrended_signal, M, lambda_scale, Mr, peaks_indices, std_dev
