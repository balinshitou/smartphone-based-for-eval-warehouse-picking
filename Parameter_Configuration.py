from pathlib import Path
import numpy as np
from Code.Algorithm.Confusion_matrix import process_all_subfolders, plot_matrix, build_accuracy_matrix

'''
Execute an automated grid search across experimental datasets to identify the optimal process (q) and 
measurement (r) noise parameters that maximize PDR distance estimation accuracy, 
outputting the best configuration and a results heatmap.
'''


def optimize_kalman_qr_params(data_dir, true_distance_val, q_values=None, r_values=None, plot=True):
    """
    Run grid search for Kalman filter  q/r parameters

    Parameters:
        data_dir (str/Path): Parent directory path containing experimental data.
        true_distance_val (float or list): True walking distance. If a float, it applies to all datasets.
        q_values (list/np.array): Search space for q values.
        r_values (list/np.array): Search space for r values.
        plot (bool): Whether to plot and save the heatmap.

    Returns:
        dict: Dict containing the optimal q value, optimal r value, maximum accuracy, and the complete result matrix.
    """
    main_path = Path(data_dir)
    if not main_path.exists():
        raise FileNotFoundError(f"Directory not found: {main_path}")

    # ===== Fetch datasets =====
    _, subfolder_total = process_all_subfolders(main_path)
    acc_datasets = subfolder_total[0]

    # ===== Format true distances =====
    if isinstance(true_distance_val, (int, float)):
        true_distances = np.array([true_distance_val] * len(acc_datasets))
    else:
        true_distances = np.array(true_distance_val)

    # ===== Set default search ranges =====
    if q_values is None:
        q_values = np.array([0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0])
    if r_values is None:
        r_values = np.array([1, 3, 5, 7, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70])

    print(f"Starting Grid Search on {len(acc_datasets)} datasets...")

    # ===== Build matrix =====
    matrix = build_accuracy_matrix(
        q_values,
        r_values,
        acc_datasets,
        true_distances
    )

    # ===== Get optimal parameters =====
    max_idx = np.unravel_index(np.argmax(matrix), matrix.shape)
    best_r = r_values[max_idx[0]]
    best_q = q_values[max_idx[1]]
    max_acc = matrix[max_idx]

    print("\n===== Optimal parameters =====")
    print(f"Best q = {best_q}")
    print(f"Best r = {best_r}")
    print(f"Max Accuracy = {max_acc:.2f}%")

    # ===== Visualization =====
    if plot:
        plot_matrix(matrix, q_values, r_values)

    return {
        "best_q": best_q,
        "best_r": best_r,
        "max_accuracy": max_acc,
        "accuracy_matrix": matrix
    }


if __name__ == "__main__":
    test_path = './Dataset/KF_Param_Tuning'
    optimize_kalman_qr_params(data_dir=test_path, true_distance_val=21.85)
