import numpy as np
from scipy.interpolate import CubicSpline

def MedianWindow(acceleration, window_size, slide_size):
    accData = []
    for i in range(0, len(acceleration), slide_size):
            accData.append(np.median(acceleration[i:i + window_size]))
    return np.array(accData)

def MedianWindow_Interpolation(time, acceleration, window_size, slide_size):
    median_acceleration = MedianWindow(acceleration, window_size, slide_size)
    acceleration_new = np.linspace(time[0], time[-1], len(median_acceleration))
    cs_clamped = CubicSpline(time[:len(acceleration) + slide_size:slide_size], median_acceleration, bc_type='clamped')
    y_clamped = cs_clamped(acceleration_new)
    return acceleration_new, y_clamped
