import numpy as np
from Code.Projects import AMPD_Peak_Detection
from Code.Projects.Butterworth import butterworth_filter_default
from Code.Projects.KalmanFilter import OneDKalmanFilter
from Code.Projects.MedianFilter import MedianWindow_Interpolation
from Code.Projects.WaveletDenoising import waveletDenoise


def _validate_sensor_timelines(time_acc, acc_x, acc_y, acc_z, time_gyro, gyro_x, gyro_y, gyro_z):
    time_acc = np.asarray(time_acc)
    time_gyro = np.asarray(time_gyro)
    if any(len(signal) != len(time_acc) for signal in (acc_x, acc_y, acc_z)):
        raise ValueError("Acceleration signals must have the same length as their timeline.")
    if any(len(signal) != len(time_gyro) for signal in (gyro_x, gyro_y, gyro_z)):
        raise ValueError("Gyroscope signals must have the same length as their timeline.")
    if len(time_acc) < 19 or len(time_gyro) < 19:
        raise ValueError("Acceleration and gyroscope timelines must each contain at least 19 samples.")
    if not np.all(np.diff(time_acc) > 0) or not np.all(np.diff(time_gyro) > 0):
        raise ValueError("Acceleration and gyroscope timelines must be monotonically increasing.")


def complementary_filter(time, gyro_data):
    """Integrate gyroscope readings using the original Euler-angle correction."""
    phi = theta = psi = 0
    gyro_data = np.asarray(gyro_data)
    time = np.asarray(time)
    angles = np.zeros_like(gyro_data, dtype=float)
    special_angles = [0, np.pi / 2, np.pi, 3 * np.pi / 2]
    for i in range(len(time)):
        dt = time[0] if i == 0 else time[i] - time[i - 1]
        cos_phi, sin_phi = np.cos(phi), np.sin(phi)
        cos_theta, tan_theta = np.cos(theta), np.tan(theta)
        phi_dot = gyro_data[i, 0] + sin_phi * tan_theta * gyro_data[i, 1] + cos_phi * tan_theta * gyro_data[i, 2]
        theta_dot = cos_phi * gyro_data[i, 1] - sin_phi * gyro_data[i, 2]
        psi_dot = sin_phi / cos_theta * gyro_data[i, 1] + cos_phi / cos_theta * gyro_data[i, 2]
        phi += phi_dot * dt
        theta += theta_dot * dt
        psi += psi_dot * dt
        if i > 0 and abs(psi - angles[i - 1, 2]) < 0.004:
            normalized_psi = psi % (2 * np.pi)
            psi = min(special_angles,
                      key=lambda angle: min(abs(normalized_psi - angle), 2 * np.pi - abs(normalized_psi - angle)))
        angles[i] = (phi, theta, psi)
    return angles


def _compute_trajectory(time_gyro, acc_z_signal, gyro_components, step_length=0.61):
    corrected_angles = complementary_filter(time_gyro, np.column_stack(gyro_components))
    _, detrended, _, _, _, peaks, _ = AMPD_Peak_Detection.ampd_algorithm(acc_z_signal)
    peak_indices = np.asarray([peak for peak in peaks if detrended[peak] > 0.2])
    north = np.zeros(len(peak_indices) + 1)
    east = np.zeros(len(peak_indices) + 1)
    rotation = np.array([[0, -1], [1, 0]])
    for index, peak in enumerate(peak_indices, start=1):
        dx = np.cos(corrected_angles[peak, 2]) * step_length
        dy = np.sin(corrected_angles[peak, 2]) * step_length
        north[index], east[index] = (north[index - 1], east[index - 1]) + rotation @ np.array([dx, dy])
    return north, east


def compute_path_comparison(time_acc, acc_x, acc_y, acc_z, time_gyro, gyro_x, gyro_y, gyro_z):
    """Return paths using median, second-stage, and Kalman-filtered signals."""
    _validate_sensor_timelines(time_acc, acc_x, acc_y, acc_z, time_gyro, gyro_x, gyro_y, gyro_z)
    window_size, slide_size = 6, 3
    fs, cutoff, order = 100, 8, 1
    kalman_args = (0, 1000, 1, 50)
    time_acc_x, mw_acc_x = MedianWindow_Interpolation(time_acc, acc_x, window_size, slide_size)
    _, mw_acc_y = MedianWindow_Interpolation(time_acc, acc_y, window_size, slide_size)
    _, mw_acc_z = MedianWindow_Interpolation(time_acc, acc_z, window_size, slide_size)
    filtered_time, mw_gyro_x = MedianWindow_Interpolation(time_gyro, gyro_x, window_size, slide_size)
    _, mw_gyro_y = MedianWindow_Interpolation(time_gyro, gyro_y, window_size, slide_size)
    _, mw_gyro_z = MedianWindow_Interpolation(time_gyro, gyro_z, window_size, slide_size)
    if len(time_acc_x) != len(filtered_time) or not np.allclose(time_acc_x, filtered_time):
        raise ValueError("Acceleration and gyroscope timelines must be aligned after filtering.")
    wavelet_gyro = tuple(waveletDenoise(filtered_time, component) for component in (mw_gyro_x, mw_gyro_y, mw_gyro_z))
    bf_acc = tuple(
        butterworth_filter_default(component, cutoff, fs, order) for component in (mw_acc_x, mw_acc_y, mw_acc_z))
    kmf_acc = tuple(
        OneDKalmanFilter(kalman_args[0], kalman_args[1], component, kalman_args[2], kalman_args[3]) for component in
        bf_acc)
    kmf_gyro = tuple(
        OneDKalmanFilter(kalman_args[0], kalman_args[1], component, kalman_args[2], kalman_args[3]) for component in
        wavelet_gyro)
    return {
        "stage_1": _compute_trajectory(filtered_time, mw_acc_z, (mw_gyro_x, mw_gyro_y, mw_gyro_z)),
        "stage_2": _compute_trajectory(filtered_time, bf_acc[2], wavelet_gyro),
        "stage_3": _compute_trajectory(filtered_time, kmf_acc[2], kmf_gyro),
    }
