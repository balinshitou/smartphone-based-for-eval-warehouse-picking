from pathlib import Path
import matplotlib.pyplot as plt
from Code.Algorithm.acc_comparison_core import compute_acc_comparison
from Code.Projects.FileLoad import read_data

'''
Load acceleration data, apply three-stage filtering, and visualize filtering effects using the Z-axis signal.
'''

data_name = "Acc_Comparison_data"


def main():
    """Load data, calculate the filter stages, and display their Z-axis plot."""
    file_name = Path("./Dataset") / data_name
    data_path = file_name / "Linear Accelerometer.csv"
    if not data_path.is_file():
        raise FileNotFoundError(f"Required data file does not exist: {data_path}")
    time_acc, acc_x, acc_y, acc_z = read_data(data_path)
    result = compute_acc_comparison(time_acc, acc_x, acc_y, acc_z)

    # Define filter stage labels and colors
    acc_labels = ['Raw Data', 'Median', 'Median + Butterworth', 'Median + Butterworth + Kalman']
    acc_colors = ['gray', 'blue', 'green', 'red', 'black']

    plt.figure(figsize=(10, 10))
    plt.plot(result["raw_time"], result["raw"][2], '--', markersize=2, color=acc_colors[0], alpha=0.5,
             label=acc_labels[0])
    plt.plot(result["time"], result["median"][2], '-', linewidth=1.5, color=acc_colors[1], label=acc_labels[1])
    plt.plot(result["time"], result["butterworth"][2], '-', linewidth=1.5, color=acc_colors[2], label=acc_labels[2])
    plt.plot(result["time"], result["kalman"][2], '-', linewidth=1.5, color=acc_colors[3], label=acc_labels[3])
    plt.xlabel("Sample")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend(loc='upper right')
    plt.show()


if __name__ == "__main__":
    main()
