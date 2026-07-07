import matplotlib.pyplot as plt

ROUTES = {
    "path_1": {
        "real_distance": 104.5,
        "points": [
            (0, 0), (0, 39.8), (-8.5, 39.8), (-8.5, 38.2),
            (-2, 38.2), (-2, 15.2), (-8.5, 15.2), (-8.5, 14.2),
            (-2, 14.2), (-2, 0),
        ],
    },
    "path_2": {
        "real_distance": 96.2,
        "points": [
            (0, 0), (0, 39.8), (-2, 39.8), (-2, 38.2), (-2, 37.2),
            (-5.35, 37.2), (-5.35, 36), (-2, 36), (-2, 5.2),
            (-5.95, 5.2), (-5.95, 4.2), (-2, 4.2), (-2, 0),
        ],
    },
    "path_3": {
        "real_distance": 96.6,
        "points": [
            (0, 0), (0, 38), (-2, 38), (-2, 15.2), (-7.35, 15.2),
            (-7.35, 14.2), (-2, 14.2), (-2, 5.2), (-5.95, 5.2),
            (-5.95, 4.2), (-2, 4.2), (-2, 0),
        ],
    },
}


def route_for_dataset(dataset_name):
    """Return the predefined route selected by a Dataset directory name."""
    for route_id in ROUTES:
        if dataset_name.startswith(route_id.replace("path_", "Path")):
            return route_id
    raise ValueError(
        f"Dataset '{dataset_name}' does not identify a predefined route. "
        "Use a name beginning with Path1, Path2, or Path3."
    )


def route_config_for_dataset(dataset_name):
    """Return the route id and immutable configuration for a dataset name."""
    route_id = route_for_dataset(dataset_name)
    return route_id, ROUTES[route_id]


def plot_warehouse_layout(route_id="path_1", ax_limits=(-45, 1, -12, 0.5)):
    """Draw one rotated predefined warehouse route."""
    try:
        path_points = ROUTES[route_id]["points"]
    except KeyError as error:
        raise ValueError(f"Unknown predefined route: {route_id}") from error

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_aspect('equal')
    for i in range(len(path_points) - 1):
        start = path_points[i]
        end = path_points[i + 1]

        # Rotate 90 degrees counter-clockwise
        start_rot = [-start[1], start[0]]
        end_rot = [-end[1], end[0]]
        ax.plot([start_rot[0], end_rot[0]], [start_rot[1], end_rot[1]],
                color='red', linestyle='-', linewidth=2,
                label='Predefined Path' if i == 0 else None)
    ax.set_xlim(ax_limits[0], ax_limits[1])
    ax.set_ylim(ax_limits[2], ax_limits[3])
    ax.grid(linestyle='--', alpha=0.7)
    return fig, ax


if __name__ == "__main__":
    fig, ax = plot_warehouse_layout("path_3")
    plt.show()
