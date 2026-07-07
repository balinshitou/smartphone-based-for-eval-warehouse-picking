import pandas as pd
from pathlib import Path

def read_data(file_path):
    data = pd.read_csv(file_path)
    time = data.iloc[:, 0].values
    acceleration_x = data.iloc[:, 1].values
    acceleration_y = data.iloc[:, 2].values
    acceleration_z = data.iloc[:, 3].values
    return time, acceleration_x, acceleration_y, acceleration_z


def read_picking_times(file_path=None):

    if file_path is None:
        current_script_path = Path(__file__).resolve()
        root_dir = current_script_path.parent.parent.parent
        csv_path = root_dir / "Dataset" /"Path1"/ "Picking-point Dwell Time.csv"
    else:
        # 如果从外部主程序传入了路径，则使用传入的路径
        csv_path = Path(file_path)

    if not csv_path.is_file():
        raise FileNotFoundError(f"❌ 找不到文件！程序试图在以下绝对路径中寻找文件: {csv_path.resolve()}")

    df = pd.read_csv(csv_path, index_col=0)  # Use 'Personnel' as the index
    # Convert DataFrame to a dictionary for quick lookup in the main loop
    picking_times_dict = {index: row.tolist() for index, row in df.iterrows()}
    return picking_times_dict