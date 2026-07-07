from pathlib import Path
import numpy as np
from collections import defaultdict
from Code.Algorithm.Predefined_Path import route_config_for_dataset
from Code.Algorithm.PDR_trajectory_core import compute_trajectory_reconstruction
from Code.Projects.FileLoad import read_data, read_picking_times

'''
Batch process acceleration and gyroscope data across multiple personnel folders.
Integrate pre-defined picking point times, calculate non-picking dwell times, 
report average metrics, and calculate normalized evaluation scores based on standard thresholds.
'''


def process_all_subfolders(main_path):
    """
    Iterate through all subfolders in the main directory.
    Returns a sorted list of Path objects for the subfolders.
    """
    main_path = Path(main_path)
    if not main_path.is_dir():
        print(f"❌ Error: The input path '{main_path}' is not a valid directory!")
        return []
    # Filter and sort subfolders
    subfolders = [f for f in main_path.iterdir() if f.is_dir()]
    return sorted(subfolders)


def main():
    # ================= Configuration Area =================
    # Please specify the directory path containing all dataset groups here
    main_folder_path = "./Dataset/Path3"

    subfolders = process_all_subfolders(main_folder_path)
    if not subfolders:
        print("⚠️ No data folders found. Exiting program.")
        return

    # Load the picking point times from the CSV file
    try:
        picking_times_dict = read_picking_times()
    except FileNotFoundError as e:
        print(e)
        return

    # Dictionary to store metrics for all personnel
    personnel_stats = defaultdict(lambda: {
        "picking_time": [],
        "picking_point_time": [],
        "non_picking_point_time": [],
        "traveling_time": [],
        "step_stride": [],
        "actual_step_length": []
    })

    current_personnel = ""
    dataset_count = 0

    # Iterate through each subfolder
    for folder in subfolders:
        data_name = folder.name

        # Parse personnel ID from folder name
        person_id = "Unknown"
        csv_person_key = "Unknown"
        for part in data_name.split('_'):
            if "Personnel" in part:
                person_id = part
                person_num = int(part.replace("Personnel", ""))
                csv_person_key = f"Personnel {person_num}"
                break

        if person_id != current_personnel:
            current_personnel = person_id
            dataset_count = 1
            print(f"\n{'=' * 25} Processing Started: {current_personnel} {'=' * 25}")
        else:
            dataset_count += 1

        print(f"\n--- Running: {current_personnel} (Dataset {dataset_count}) | Folder: {data_name} ---")

        acceleration_path = folder / "Linear Accelerometer.csv"
        gyroscope_path = folder / "Gyroscope.csv"

        if not acceleration_path.is_file() or not gyroscope_path.is_file():
            print(f"⚠️ Skipping {data_name}: Missing required sensor data files.")
            continue

        # 1. Read data and configurations
        route_id, route_config = route_config_for_dataset(data_name)
        time_acc, acc_x, acc_y, acc_z = read_data(acceleration_path)
        time_gyro, gyro_x, gyro_y, gyro_z = read_data(gyroscope_path)

        # 2. Calculate core trajectory and Picking Time
        picking_time = time_acc[-1]
        print(f"Order Picking Time: {picking_time:.2f} s")

        result = compute_trajectory_reconstruction(
            time_acc, acc_x, acc_y, acc_z,
            time_gyro, gyro_x, gyro_y, gyro_z,
            real_distance=route_config["real_distance"]
        )

        # 3. Calculate Dwell Times and Traveling Time
        static_periods = result.get("static_periods", [])
        filtered_time = result.get("filtered_time", [])
        total_dwell_time = 0.0

        for start, end in static_periods:
            duration = filtered_time[end] - filtered_time[start]
            total_dwell_time += duration

        traveling_time = picking_time - total_dwell_time

        trial_index = dataset_count - 1
        try:
            picking_point_time = picking_times_dict[csv_person_key][trial_index]
        except (KeyError, IndexError):
            picking_point_time = 0.0

        non_picking_point_time = total_dwell_time - picking_point_time

        step_stride = result['step_length']
        actual_step_length = result['walking_distance']

        print(f"Total Dwell Time: {total_dwell_time:.3f} s")
        print(f"-> Picking Point Time: {picking_point_time:.3f} s")
        print(f"-> Non-picking Point Time: {non_picking_point_time:.3f} s")
        print(f"Traveling Time: {traveling_time:.3f} s")
        print(f"Actual Step Length: {actual_step_length:.4f} m")

        # 4. Save current group data to the dictionary
        personnel_stats[person_id]["picking_time"].append(round(picking_time, 2))
        personnel_stats[person_id]["picking_point_time"].append(round(picking_point_time, 2))
        personnel_stats[person_id]["non_picking_point_time"].append(round(non_picking_point_time, 2))
        personnel_stats[person_id]["traveling_time"].append(round(traveling_time, 2))
        personnel_stats[person_id]["step_stride"].append(round(step_stride, 2))
        personnel_stats[person_id]["actual_step_length"].append(round(actual_step_length, 2))

    # ================= Output Final Statistical Tables =================
    if not personnel_stats:
        return

    personnel_list = sorted(list(personnel_stats.keys()))

    # ---------------- TABLE 1: RAW AVERAGES ----------------
    line_length_raw = 40 + len(personnel_list) * 18
    print("\n\n" + "=" * line_length_raw)
    print("Table 1: Final Statistical Results (Raw Averages)".center(line_length_raw))
    print("=" * line_length_raw)

    row_format_raw = "{:<40}" + "".join([" | {:<15}"] * len(personnel_list))
    print(row_format_raw.format("Indicator", *personnel_list))
    print("-" * line_length_raw)

    metrics_raw = [
        ("Order Picking Time (s)", "picking_time", 3),
        ("Picking-point Dwell Time (s)", "picking_point_time", 3),
        ("System-unauthorized Stagnation Time (s)", "non_picking_point_time", 3),
        ("Travelling Time (s)", "traveling_time", 3),
        ("Actual Picking Path Length (m)", "actual_step_length", 3)
    ]

    # Pre-calculate averages to use in both tables
    averages_dict = {person: {} for person in personnel_list}

    for display_name, dict_key, decimals in metrics_raw:
        row_values = [display_name]
        for person in personnel_list:
            stats = personnel_stats[person][dict_key]
            avg_value = np.mean(stats) if stats else 0
            averages_dict[person][dict_key] = avg_value
            row_values.append(f"{avg_value:.{decimals}f}")
        print(row_format_raw.format(*row_values))
        print("-" * line_length_raw)
    print("=" * line_length_raw)

    # ---------------- TABLE 2: NORMALIZED SCORES ----------------
    # Line length adjusted for the new 'Weight' column
    line_length_score = 40 + 10 + len(personnel_list) * 18
    print("\n\n" + "=" * line_length_score)
    print("Table 2: Normalized Evaluation Scores".center(line_length_score))
    print("=" * line_length_score)

    row_format_score = "{:<40} | {:<8}" + "".join([" | {:<15}"] * len(personnel_list))
    print(row_format_score.format("Indicator", "Weight", *personnel_list))
    print("-" * line_length_score)

    # Standard configuration: (Display Name, Dict Key, Satisfactory, Threshold, Weight)
    standards = [
        ("Order Picking Time (s)", "picking_time", 154.4, 231.63, 0.10),
        ("Picking-point Dwell Time (s)", "picking_point_time", 64.0, 96.0, 0.30),
        ("System-unauthorized Stagnation Time (s)", "non_picking_point_time", 0.0, 11.0, 0.40),
        ("Travelling Time (s)", "traveling_time", 90.4, 135.63, 0.10),
        ("Actual Picking Path Length (m)", "actual_step_length", 104.5, 114.95, 0.10)
    ]

    total_scores = {person: 0.0 for person in personnel_list}

    for display_name, dict_key, sat, thresh, weight in standards:
        # Convert weight to percentage string (e.g., 0.10 -> "10%")
        row_values = [display_name, f"{weight:.0%}"]

        for person in personnel_list:
            actual_avg = averages_dict[person][dict_key]

            # Calculate score: (Actual - Threshold) / (Satisfactory - Threshold)
            # Added safeguard to prevent division by zero
            if sat != thresh:
                normalized_score = (actual_avg - thresh) / (sat - thresh) * 40 + 60
            else:
                normalized_score = 0.0

            # Accumulate weighted score
            total_scores[person] += (normalized_score * weight)

            # Append formatted score (retaining 4 decimal places for precision)
            row_values.append(f"{normalized_score:.4f}")

        print(row_format_score.format(*row_values))
        print("-" * line_length_score)

    # Append the Total Score row
    total_row = ["Total Score", "100%"]
    for person in personnel_list:
        total_row.append(f"{total_scores[person]:.4f}")

    print(row_format_score.format(*total_row))
    print("=" * line_length_score)


if __name__ == "__main__":
    main()