import numpy as np
from Code.Projects import AMPD_Peak_Detection
from Code.Projects.Butterworth import butterworth_filter_default
from Code.Projects.KalmanFilter import OneDKalmanFilter
from Code.Projects.MedianFilter import MedianWindow_Interpolation
from Code.Projects.WaveletDenoising import waveletDenoise
from Code.Algorithm.path_comparison_core import _validate_sensor_timelines, complementary_filter
from Code.Algorithm.StepStride import compute_step_metrics


def detect_static_periods(acceleration_data, threshold=0.2, min_length=50):
    static_indices = np.where(np.abs(acceleration_data) < threshold)[0]
    periods = []
    start = 0
    for i in range(1, len(static_indices)):
        if static_indices[i] != static_indices[i - 1] + 1:
            if i - start >= min_length:
                periods.append((static_indices[start], static_indices[i - 1]))
            start = i
    if len(static_indices) - start >= min_length:
        periods.append((static_indices[start], static_indices[-1]))
    return periods


def compute_trajectory_reconstruction(time_acc, acc_x, acc_y, acc_z, time_gyro, gyro_x, gyro_y, gyro_z,
                                      real_distance=104.5):
    """Return the original trajectory-reconstruction outputs without external I/O."""
    _validate_sensor_timelines(time_acc, acc_x, acc_y, acc_z, time_gyro, gyro_x, gyro_y, gyro_z)
    window_size, slide_size = 6, 3
    time_acc_x, mw_acc_x = MedianWindow_Interpolation(time_acc, acc_x, window_size, slide_size)
    _, mw_acc_y = MedianWindow_Interpolation(time_acc, acc_y, window_size, slide_size)
    _, mw_acc_z = MedianWindow_Interpolation(time_acc, acc_z, window_size, slide_size)
    filtered_time, mw_gyro_x = MedianWindow_Interpolation(time_gyro, gyro_x, window_size, slide_size)
    _, mw_gyro_y = MedianWindow_Interpolation(time_gyro, gyro_y, window_size, slide_size)
    _, mw_gyro_z = MedianWindow_Interpolation(time_gyro, gyro_z, window_size, slide_size)
    if len(time_acc_x) != len(filtered_time) or not np.allclose(time_acc_x, filtered_time):
        raise ValueError("Acceleration and gyroscope timelines must be aligned after filtering.")
    wavelet_gyro = tuple(waveletDenoise(filtered_time, signal) for signal in (mw_gyro_x, mw_gyro_y, mw_gyro_z))
    bf_acc_z = butterworth_filter_default(mw_acc_z, 8, 100, 1)
    kmf_acc_z = OneDKalmanFilter(0, 1000, bf_acc_z, 1, 50)
    kmf_gyro = tuple(OneDKalmanFilter(0, 1000, signal, 1, 50) for signal in wavelet_gyro)
    corrected_angles = complementary_filter(filtered_time, np.column_stack(kmf_gyro))
    static_periods = detect_static_periods(kmf_acc_z)
    durations = [time_acc_x[end] - time_acc_x[start] for start, end in static_periods]
    _, detrended, _, _, _, peaks, _ = AMPD_Peak_Detection.ampd_algorithm(kmf_acc_z)
    peak_indices = np.asarray([peak for peak in peaks if detrended[peak] > 0.2])
    step_length = compute_step_metrics(peak_indices, kmf_acc_z)['average_step_length']
    north, east = np.zeros(len(peak_indices) + 1), np.zeros(len(peak_indices) + 1)
    rotation = np.array([[0, -1], [1, 0]])
    for index, peak in enumerate(peak_indices, start=1):
        dx, dy = np.cos(corrected_angles[peak, 2]) * step_length, np.sin(corrected_angles[peak, 2]) * step_length
        north[index], east[index] = (north[index - 1], east[index - 1]) + rotation @ np.array([dx, dy])
    walking_distance = step_length * len(peak_indices)
    if len(peak_indices) == 0:
        walking_distance = error = error_rate = 0.0
    else:
        error = walking_distance - real_distance
        error_rate = error / real_distance
    return {
        "north": north, "east": east, "static_periods": static_periods, "durations": durations,
        "step_count": len(peak_indices), "step_length": step_length, "walking_distance": walking_distance,
        "error": error, "error_rate": error_rate, "duration_seconds": time_acc_x[-1],
        "peak_indices": peak_indices, "filtered_time": time_acc_x,
    }
