from pathlib import Path
import matplotlib.pyplot as plt
from Code.Algorithm.path_comparison_core import compute_path_comparison
from Code.Algorithm.Predefined_Path import plot_warehouse_layout, route_for_dataset
from Code.Projects.FileLoad import read_data


'''
Load acceleration and gyroscope data, compute PDR trajectories under different filtering stages, and compare them with the reference path.
'''

data_name = "Path2_Personnel1_01"

def main():
    """Load sensor data, compare filtering stages, and display their paths."""
    file_name = Path("./Dataset/Path2") /data_name
    acceleration_path = file_name / "Linear Accelerometer.csv"
    gyroscope_path = file_name / "Gyroscope.csv"
    for path in (acceleration_path, gyroscope_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required data file does not exist: {path}")
    time_acc, acc_x, acc_y, acc_z = read_data(acceleration_path)
    time_gyro, gyro_x, gyro_y, gyro_z = read_data(gyroscope_path)
    result = compute_path_comparison(time_acc, acc_x, acc_y, acc_z, time_gyro, gyro_x, gyro_y, gyro_z)

    _, axis = plot_warehouse_layout(route_for_dataset(data_name))
    for (stage, (north, east)), color, label in zip(
            result.items(), ("limegreen", "royalblue", "darkorange"),
            ("Stage 1", "Stage 1 + Stage 2", "Stage 1 + Stage 2 +Stage 3"),
    ):
        del stage
        axis.plot(-east, north, color=color, linewidth=1.5, label=label)
    axis.set_xlabel("X Coordinate (meters)")
    axis.set_ylabel("Y Coordinate (meters)")
    axis.grid(linestyle="--", alpha=0.7)
    axis.grid()
    axis.legend()
    plt.show()


if __name__ == "__main__":
    main()
