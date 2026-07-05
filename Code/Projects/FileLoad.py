import pandas as pd


def read_data(file_path):
    data = pd.read_csv(file_path)
    time = data.iloc[:, 0].values
    acceleration_x = data.iloc[:, 1].values
    acceleration_y = data.iloc[:, 2].values
    acceleration_z = data.iloc[:, 3].values
    return time, acceleration_x, acceleration_y, acceleration_z
