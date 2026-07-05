import numpy as np


def compute_step_metrics(peaks_indices, acc_kf, p=0.45, k=0.9):
    """
    Estimates step lengths and validates peaks using the weighted Kim step length algorithm.

    This function isolates acceleration segments between consecutive peaks
    to dynamically compute the step length, filtering out invalid steps based
    on empirical amplitude thresholds.

    Args:
        peaks_indices (np.ndarray or list): Indices of detected peaks in the signal.
        acc_kf (np.ndarray): 1D array of Kalman-filtered acceleration data (typically the Z-axis).
        p (float, optional): Weighting factor controlling the influence of the
            previous step length. Defaults to 0.45.
        k (float, optional): Scaling constant for the Kim step length estimation
            model. Defaults to 0.9.

    Returns:
        dict or None: A dictionary containing the step metrics, or None if
            insufficient peaks are detected.
            Format: {
                "average_step_length": float,
                "step_lengths": list[float],
                "valid_peaks": list[int]
            }
    """

    # Initialize the first step length with a typical human step length (in meters)
    current_step_length = np.random.uniform(0.6, 0.75)

    def _calculate_kim_step(acc_segment, prev_step_len):
        """
        Internal helper: Computes step length using the weighted Kim empirical formula.
        Note: The leading underscore '_' denotes this as a private helper function.
        """
        sum_abs_acc = np.sum(np.abs(acc_segment))
        estimated_length = p * prev_step_len + (1 - p) * k * (sum_abs_acc / len(acc_segment)) ** (1 / 3)
        return estimated_length

    step_lengths = []
    valid_peaks = []

    # Check for insufficient peaks to define even a single step interval
    if len(peaks_indices) < 2:
        print("Warning: Insufficient peaks detected. Unable to calculate stride length.")
        return None

    # Iterate through adjacent peak pairs to analyze each step cycle
    for i in range(1, len(peaks_indices)):
        start_idx, end_idx = peaks_indices[i - 1], peaks_indices[i]
        acc_segment = acc_kf[start_idx:end_idx]

        # Validate the step segment based on amplitude characteristics.
        # Thresholds (0.2 to 2.5 m/s^2) are empirically set to reject noise and non-walking movements.
        if len(acc_segment) > 1:
            amplitude = np.max(acc_segment) - np.min(acc_segment)
            if 0.2 <= amplitude <= 2.5:
                current_step_length = _calculate_kim_step(acc_segment, current_step_length)
                step_lengths.append(current_step_length)
                valid_peaks.append(peaks_indices[i])

    # Calculate the average step length, handling the case where no valid steps were found
    average_step_length = np.mean(step_lengths) if step_lengths else 0.0

    return {
        "average_step_length": average_step_length,
        "step_lengths": step_lengths,
        "valid_peaks": valid_peaks
    }
