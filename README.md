We proposed a reproducible analysis package for smartphone-sensor data collected during warehouse picking. It organizes multi-sensor trajectory datasets, compares successive denoising strategies for acceleration, and reconstructs pedestrian dead-reckoning trajectories by combining filtered acceleration signals, gyroscope-based orientation estimation, and multiscale step detection. The package automatically connects a selected dataset to its corresponding predefined warehouse path and reference path length, allowing reconstructed trajectories and path-length errors to be visualized with minimal user configuration; within the same personnel performance evaluation framework, these trajectory-derived indicators and sensor measurements can also be used to assess and classify workers and to support corresponding management measures.

## Overview

This project provides reproducible processing and visualization tools for smartphone-sensor trajectories collected during warehouse-picking activities. The workflow compares denoising stages for acceleration, reconstructs pedestrian trajectories from accelerometer and gyroscope data, and compares the reconstructed trajectories obtained under different filtering stages against the corresponding predefined reference path. For ease of review and reproduction, the runnable scripts are placed in the root `Data_and_Code/` directory; you normally only need to modify `data_name` before running an analysis script.

## Prerequisites

This project was developed and tested using Python 3.6. Before running the core PDR algorithm or performing parameter optimization-related main functions, ensure that the necessary dependencies are configured.

Additionally, the primary libraries used in this project have been listed in `requirements.txt`.For a complete list of all dependencies and their exact version numbers required to reproduce the experimental results, please refer to this document.

## Directory organisation

```text
Data_and_Code/
├── Code/
│   ├── Algorithm/             # core analysis algorithms and path definitions
│   └── Projects/              # reusable processing utilities
├── Dataset/
│   ├── Acc_Comparison_data/   # dataset used for acceleration-filter comparison
		├── KF_Param_Tuning/			 # dataset used for Kalman filter parameter tuning
│   ├── Path1_.../             # path-1 trajectory datasets
│   ├── Path2_.../             # path-2 trajectory datasets
│   └── Path3_.../             # path-3 trajectory datasets
├── Acc_Comparison.py          # compares filtering stages for acceleration signals
├── Path_Comparison.py         # compares trajectories under different filtering stages
├── PDR_Trajectory.py          # reconstructs one PDR trajectory and reports metrics
├── Parameter_Configuration.py # finds suitable Kalman filter parameters using grid search
└── README.md                  # project guide
```

This project is organized around three main components: `Dataset/`, which stores the smartphone-sensor records; `Code/`, which contains core algorithms and reusable processing utilities; and the runnable scripts (`Acc_Comparison.py`, `Path_Comparison.py`, `PDR_Trajectory.py`). The `Dataset/` directory currently contains one acceleration-comparison dataset,  4 experimental datasets are provided for the purpose of Kalman filtering parameter optimization, and 46 path-structured trajectory datasets across three predefined reference paths.

## Runnable Scripts

| File                         | Function                                                     |
| ---------------------------- | :----------------------------------------------------------- |
| `Acc_Comparison.py`          | Loads acceleration data, processes it through three-stage filtering, and visualizes the filtering effects at different stages using the Z-axis signal. |
| `Path_Comparison.py`         | Loads acceleration and gyroscope data, calculates PDR trajectories under different filtering stages, automatically selects the matching predefined reference path, and visualizes the comparison of reconstructed PDR trajectories across filtering stages. |
| `PDR_Trajectory.py`          | Reconstructs one PDR trajectory, automatically selects the matching reference length, prints duration/step/distance/error metrics, and displays the reconstructed path and holding points. |
| `Parameter_Configuration.py` | Automatically loads all sub-datasets from the specified directory, evaluates each `q/r` combination, reports the optimal parameters, and optionally generates an accuracy heatmap. |

The workflow of the runnable scripts links dataset selection, sensor-data loading, filtering, step detection, trajectory reconstruction, and reference-path comparison into a single reproducible analysis sequence. After a dataset is specified, the scripts automatically locate the corresponding sensor files, apply the implemented processing stages, reconstruct the PDR trajectory, and report trajectory-level metrics relative to the selected reference path.

```text
Choose data_name
        ↓
Locate Dataset/<data_name> automatically
        ↓
Load Linear Accelerometer.csv
        ├── Acc_Comparison: compare filter stages and display Z-axis signals
        └── Path_Comparison / PDR_Trajectory: also load Gyroscope.csv
                                      ↓
                        Median filtering → second-stage filtering → Kalman filtering
                                      ↓
                 AMPD peak detection + gyroscope orientation integration
                                      ↓
        Identify the path from the Path1/Path2/Path3 prefix in the dataset name
                                      ↓
                           Reconstruct the PDR path
                                      ↓
   Compare the reference path with the reconstructed PDR trajectory and report metrics
```

## Processing utility modules

The processing utility modules in `Code/Projects/` provide reusable signal-processing and data-loading functions that are shared by the algorithm modules.

| File                     | Function                                                     |
| ------------------------ | ------------------------------------------------------------ |
| `FileLoad.py`            | Reads a three-axis sensor CSV and returns time, X, Y, and Z arrays from its first four columns. |
| `MedianFilter.py`        | Calculates sliding-window medians and uses a clamped cubic spline to interpolate the reduced series onto an output timeline. |
| `Butterworth.py`         | Creates and applies a digital Butterworth low-pass filter using SciPy. |
| `WaveletDenoising.py`    | Applies db4 wavelet decomposition, soft thresholding, and reconstruction to a signal. |
| `KalmanFilter.py`        | Implements a scalar recursive Kalman filter for one-dimensional measurement sequences. |
| `AMPD_Peak_Detection.py` | Implements multiscale peak detection: detrending, local-maxima scalogram construction, scale selection, and peak extraction. It also includes an optional visualization function. |

## Algorithm modules

The algorithm modules in `Code/Algorithm` define the core computational logic used by the runnable entry points. They separate trajectory reconstruction, path comparison, path selection, and layout visualization from file-loading utilities and runnable scripts.

| File                      | Function                                                     |
| ------------------------- | ------------------------------------------------------------ |
| `acc_comparison_core.py`  | Defines `compute_acc_comparison()`. It takes the loaded time and three-axis acceleration arrays as input and returns the raw, median, Butterworth-filtered, and Kalman-filtered signal stages. |
| `path_comparison_core.py` | Defines sensor-timeline validation, gyroscope orientation integration, step-based coordinate updates, and `compute_path_comparison()`, which returns three trajectories under different filtering stages. |
| `PDR_trajectory_core.py`  | Defines static-period detection, step-length estimation, and `compute_trajectory_reconstruction()`. The function returns coordinates, step-related values, holding periods, duration, walking distance, and error metrics. |
| `Predefined_Path.py`      | Stores the point sequences and reference lengths of the three paths. It maps dataset-name prefixes to the corresponding path and draws the selected path. |
| `Warehouse_Layout.py`     | Draws a detailed warehouse layout with explicit shelf positions and can additionally display the picking points, standard path, and directional arrows for Path 1. |
| `Calibration_Layout.py`   | Draws a smaller calibration-layout figure with shelves, inbound/outbound points, picking points, arrows, and annotated distances. |
| `StepStride.py`           | Estimates step length from detected step peaks and Kalman_filtered acceleration signals. |
| `Confusion_matrix.py`     | This script reads `Linear Accelerometer.csv` and `Gyroscope.csv`, with the linear acceleration signal used for gait analysis. The acceleration signal is processed through median-window interpolation, Butterworth low-pass filtering, and one-dimensional Kalman filtering. The AMPD peak detection algorithm is then applied to identify gait-related peaks, and a dynamic step-length model is used to estimate the total walking distance. The estimated distance is compared with the true distance to calculate the accuracy for each parameter combination. |