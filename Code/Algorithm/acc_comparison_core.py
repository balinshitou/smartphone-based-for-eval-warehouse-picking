import numpy as np
from Code.Projects.Butterworth import butterworth_filter_default
from Code.Projects.KalmanFilter import OneDKalmanFilter
from Code.Projects.MedianFilter import MedianWindow_Interpolation


def compute_acc_comparison(time_acc, acc_x, acc_y, acc_z):
    """Return the raw and progressively filtered acceleration components."""
    window_size = 6
    slide_size = 3
    fs = 100
    cutoff = 8
    order = 1
    initial_value = 0
    initial_probability = 1000
    process_variance = 1
    measurement_variance = 50

    # 1. Define a unified slice object for the target range
    start_idx = 817
    end_idx = 950
    target_slice = slice(start_idx, end_idx)

    # 2. Convert raw data to numpy arrays and pack them into a tuple for batch processing
    raw_acc = (np.asarray(acc_x), np.asarray(acc_y), np.asarray(acc_z))
    time_acc = np.asarray(time_acc)

    # 3. Median filtering and interpolation
    # (Unpacked explicitly to clearly assign the filtered time axis)
    _, median_x = MedianWindow_Interpolation(time_acc, raw_acc[0], window_size, slide_size)
    _, median_y = MedianWindow_Interpolation(time_acc, raw_acc[1], window_size, slide_size)
    filtered_time, median_z = MedianWindow_Interpolation(time_acc, raw_acc[2], window_size, slide_size)

    # Repack the median-filtered 3-axis data
    median_acc = (median_x, median_y, median_z)

    # 4. Batch filtering core: Apply independent filtering across all axes using comprehensions
    butterworth = tuple(butterworth_filter_default(c, cutoff, fs, order) for c in median_acc)
    kalman = tuple(
        np.asarray(OneDKalmanFilter(initial_value, initial_probability, c, process_variance, measurement_variance))
        for c in butterworth
    )

    # 5. Simplified return dictionary: Use comprehensions for batch slicing
    return {
        "raw_time": time_acc[2451:2850],
        "time": filtered_time[target_slice],
        "raw": tuple(c[2451:2850].copy() for c in raw_acc),
        "median": tuple(c[target_slice] for c in median_acc),
        "butterworth": tuple(c[target_slice] for c in butterworth),
        "kalman": tuple(c[target_slice] for c in kalman),
    }
