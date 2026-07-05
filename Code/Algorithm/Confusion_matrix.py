import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from Code.Projects import AMPD_Peak_Detection
from natsort import humansorted
from Code.Projects.Butterworth import butterworth_filter_default
from Code.Projects.FileLoad import read_data
from Code.Projects.KalmanFilter import OneDKalmanFilter
from Code.Projects.MedianFilter import MedianWindow_Interpolation

'''
Implement a complete IMU-based step stride and distance estimation pipeline, 
featuring filter preprocessing , such as Median filtering, Butterworth low-pass filter and 1 D Kalman filtering, 
and AMPD peak detection. It also builds the evaluation matrix for q/r parameter accuracy.
'''


# read all subfolders
def process_all_subfolders(MAIN_PATH):
    subfolders = [f for f in MAIN_PATH.iterdir() if f.is_dir()]
    sorted_subfolders = humansorted(subfolders, key=lambda x: x.name)

    column = len(sorted_subfolders)

    subfolder_name = np.array([None] * column, dtype=object)
    subfolder_total = np.array([[None] * column, [None] * column], dtype=object)

    for idx, subfolder in enumerate(sorted_subfolders):
        subfolder_name[idx] = subfolder.name
        acc_csv_path = subfolder / 'Linear Accelerometer.csv'
        gyro_csv_path = subfolder / 'Gyroscope.csv'
        subfolder_total[0][idx] = str(acc_csv_path)
        subfolder_total[1][idx] = str(gyro_csv_path)
    return subfolder_name, subfolder_total


# Step stride calculation function
def calculate_step_length(acc_data, L_k_minus_1, p=0.4, k=0.9):
    a_sum = np.sum(np.abs(acc_data))
    step_length = p * L_k_minus_1 + (1 - p) * k * (a_sum / len(acc_data)) ** (1 / 3)
    return step_length


def compute_distance_single(data_path, q, r):
    # ===== read Data =====
    time, acc_x, acc_y, acc_z = read_data(data_path)
    # ===== Median filter =====
    window_size, slide_size = 6, 3
    z_new, acc_z_mw = MedianWindow_Interpolation(time, acc_z, window_size, slide_size)
    # ===== Butterworth =====
    fs, cutoff, order = 100, 8, 1
    acc_z_bf = butterworth_filter_default(acc_z_mw, cutoff, fs, order)
    # ===== Kalman filter =====
    initial_value, initial_probability = 0, 1000
    kmf_acc_z = OneDKalmanFilter(initial_value, initial_probability, acc_z_bf, q, r)
    # ===== peak detection =====
    signal_z, detrended_signal_z, M_z, lambda_z, Mr_z, peaks_indices_z, std_dev_z = AMPD_Peak_Detection.ampd_algorithm(
        kmf_acc_z)

    step_lengths = []
    valid_peaks = []
    L_k_minus_1 = np.random.uniform(0.6, 0.75)
    if len(peaks_indices_z) < 2:
        print("Too few peaks to calculate step frequency.")
    else:
        for i in range(1, len(peaks_indices_z)):
            start, end = peaks_indices_z[i - 1], peaks_indices_z[i]
            acc_pv = kmf_acc_z[start:end]
            if len(acc_pv) > 1 and 0.2 <= np.max(acc_pv) - np.min(acc_pv) <= 2.5:
                step_length = calculate_step_length(acc_pv, L_k_minus_1)
                step_lengths.append(step_length)
                valid_peaks.append(peaks_indices_z[i])
                L_k_minus_1 = step_length
    step_length = np.mean(step_lengths)
    peak_num_indices = []
    for i in range(len(peaks_indices_z)):
        if detrended_signal_z[peaks_indices_z[i]] > 0.2:
            peak_num_indices.append(peaks_indices_z[i])
    peak_num_z = len(peak_num_indices)
    walking_distance = step_length * peak_num_z
    return walking_distance


# Average accuracy across multiple datasets
def compute_dataset_accuracy(q, r, acc_datasets, true_distances):
    accuracies = []
    for i, data_path in enumerate(acc_datasets):
        est_distance = compute_distance_single(data_path, q, r)
        real_distance = true_distances[i]
        error_rate = abs(est_distance - real_distance) / real_distance
        accuracy = (1 - error_rate) * 100
        accuracy = max(0, accuracy)
        accuracies.append(accuracy)
    return np.mean(accuracies)


# ======Build accuracy matrix======
def build_accuracy_matrix(q_values, r_values, acc_datasets, true_distances):
    matrix = np.zeros((len(r_values), len(q_values)))
    for i, r in enumerate(r_values):
        for j, q in enumerate(q_values):
            avg_accuracy = compute_dataset_accuracy(
                q, r,
                acc_datasets,
                true_distances
            )
            matrix[i, j] = avg_accuracy
            print(f"q={q:.3f}, r={r:.3f}, Avg Accuracy={avg_accuracy:.2f}%")

    return matrix


# Plot heatmap
def plot_matrix(matrix, q_values, r_values, save_path="accuracy_heatmap.png"):
    plt.figure(figsize=(10, 6))

    ax = sns.heatmap(
        matrix,
        xticklabels=np.round(q_values, 3),
        yticklabels=np.round(r_values, 3),
        cmap='gray',
        vmin=80,
        vmax=100,
        cbar_kws={'label': 'Accuracy (%)'}
    )

    # ===== Mark selected parameters （q=1，r=50）=====
    q_target = 1
    r_target = 50

    try:
        q_idx = list(q_values).index(q_target)
        r_idx = list(r_values).index(r_target)

        ax.add_patch(plt.Rectangle(
            (q_idx, r_idx), 1, 1,
            fill=False,
            edgecolor='red',
            linewidth=2
        ))

        # -------- (Optional) Add numerical labels. --------
        value = matrix[r_idx, q_idx]
        ax.text(
            q_idx + 0.5, r_idx + 0.5,
            f"{value:.1f}%",
            ha='center', va='center',
            color='red',
            fontsize=10,
            fontweight='bold'
        )

    except ValueError:
        pass

    plt.xlabel('q (Process Variance)')
    plt.ylabel('r (Measurement Variance)')
    plt.title('Accuracy Heatmap')
    plt.xticks(rotation=0)
    plt.yticks(rotation=0)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, format="png", bbox_inches="tight")
        print(f"Heatmap saved to {save_path}")
    plt.show()
