from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from Code.Algorithm.Warehouse_Layout import plot_warehouse_layout
from Code.Algorithm.Predefined_Path import route_config_for_dataset
from Code.Algorithm.PDR_trajectory_core import compute_trajectory_reconstruction
from Code.Projects.FileLoad import read_data

'''
Load acceleration and gyroscope data, reconstruct one PDR trajectory, and report trajectory-level metrics against the reference path.
'''

data_name = "Path1_Personnel1_01_163"


def main():
    """Load data, reconstruct the trajectory, print metrics, and display it."""
    file_name = Path("./Dataset/Path1") / data_name
    acceleration_path = file_name / "Linear Accelerometer.csv"
    gyroscope_path = file_name / "Gyroscope.csv"
    for path in (acceleration_path, gyroscope_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required data file does not exist: {path}")
    route_id, route_config = route_config_for_dataset(data_name)
    time_acc, acc_x, acc_y, acc_z = read_data(acceleration_path)
    print(f"Picking Time: {time_acc[-1]:2f} s")
    time_gyro, gyro_x, gyro_y, gyro_z = read_data(gyroscope_path)
    result = compute_trajectory_reconstruction(time_acc, acc_x, acc_y, acc_z, time_gyro, gyro_x, gyro_y, gyro_z,
                                               real_distance=route_config["real_distance"])

    print(f"Duration: {result['duration_seconds']:.2f} s")
    print(f"dwell count: {len(result['static_periods'])}")
    print(f"Step count: {result['step_count']}")
    print(f"Step length: {result['step_length']:.4f} m")
    print(f"Walking distance: {result['walking_distance']:.4f} m")
    print(f"Error: {result['error']:.4f} m")
    print(f"Error rate: {result['error_rate']:.2%}")

    _, ax = plot_warehouse_layout()
    north, east = result["north"], result["east"]
    ax.plot(north, east, color="limegreen", linewidth=1.5, label="PDR path")
    static_periods = result.get("static_periods", [])
    valid_peaks = result.get("peak_indices", [])
    for idx, (start, end) in enumerate(static_periods):
        step_idx = np.searchsorted(valid_peaks, start)
        point = min(step_idx, len(north) - 1)
        label_text = "Hold point" if idx == 0 else None
        ax.plot(north[point], east[point], "r*", markersize=10, label=label_text)
        duration = result['filtered_time'][end] - result['filtered_time'][start]
        print(f"{duration}")
        ax.annotate(f"{duration:.2f} s", (north[point], east[point]))
    ax.set_xlabel("X Coordinate (meters)")
    ax.set_ylabel("Y Coordinate (meters)")
    ax.set_title("Trajectory Reconstruction")
    ax.grid(linestyle="--", alpha=0.7)
    ax.legend()
    plt.show()


if __name__ == "__main__":
    main()
