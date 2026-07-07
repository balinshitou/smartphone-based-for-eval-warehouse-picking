import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot_warehouse_layout(
        warehouse_length=45,
        warehouse_width=12,
        shelf_length=1.9,
        shelf_width=0.6,
        right_start=(0.2, 0),
        right_count=20,
        left_start_ur=(-6.4, 38),
        horizontal_units=3,
        vertical_interval=2,
        ax_limits=(-10, 3, -2, 50)
):
    fig, ax = plt.subplots(figsize=(warehouse_width / 2, warehouse_length / 3))
    ax.set_aspect('equal')

    # Draw Right Shelves
    for i in range(right_count):
        ax.add_patch(Rectangle(
            (right_start[0], right_start[1] + i * shelf_length),
            shelf_width, shelf_length,
            edgecolor='black'
        ))

    # Draw Left Shelves
    def _draw_left_shelves(start_ur):
        x_ur, y_ur = start_ur
        x_ll = x_ur - shelf_length
        y_ll = y_ur - shelf_width

        while y_ll > -shelf_width:
            for i in range(horizontal_units):
                ax.add_patch(Rectangle(
                    (x_ll + i * shelf_length, y_ll),
                    shelf_length, shelf_width,
                    edgecolor='black',
                    label='Shelves' if (y_ll > 37 and i == 0) else None
                ))
            y_ll -= vertical_interval

    _draw_left_shelves(left_start_ur)

    new_row_start_x = -8.3
    new_row_start_y = 40
    for i in range(horizontal_units):
        ax.add_patch(Rectangle(
            (new_row_start_x + i * shelf_length, new_row_start_y),
            shelf_length, shelf_width,
            edgecolor='black'
        ))

    # special_points = [
    #     (0.2, 5.5),  # a
    #     (0.2, 16.2),  # b
    #     (0.2, 23.7),  # c
    #     (0.2, 33),  # d
    #     (-3.8, 40),  # e
    #     (-7.6, 38),  # f
    #     (-7.2, 15.4),  # g
    #     (-7, 14)  # h
    # ]
    #
    # # Draw green marker points and add letter annotations
    # for i, (x, y) in enumerate(special_points):
    #     ax.scatter(x, y, s=25, color='limegreen', marker='o',
    #                label='Pick up point' if i == 0 else None,
    #                zorder=10)
    #
    #     # Add letter annotations
    #     label = chr(97 + i)  # a-h
    #     ax.text(x + 0.2, y - 0.5, label,
    #             fontsize=15, color='r',
    #             ha='left', va='bottom', zorder=11)
    #
    # path_points = [
    #     (0, 0), (0, 39.8), (-8.5, 39.8), (-8.5, 38.2),
    #     (-2, 38.2), (-2, 15.2), (-8.5, 15.2), (-8.5, 14.2),
    #     (-2, 14.2), (-2, 0)
    # ]
    #
    # for i in range(len(path_points) - 1):
    #     start = path_points[i]
    #     end = path_points[i + 1]
    #
    #     ax.plot([start[0], end[0]], [start[1], end[1]],
    #             color='red', linestyle='--', linewidth=1.5,
    #             label='Standard Path' if i == 0 else None)
    #
    #     # Add directional arrow
    #     ax.annotate('',
    #                 xytext=(start[0], start[1]),
    #                 xy=(end[0], end[1]),
    #                 arrowprops=dict(
    #                     arrowstyle="->",
    #                     color="darkred",
    #                     lw=1.5,
    #                     shrinkA=5,
    #                     shrinkB=5
    #                 ),
    #                 annotation_clip=False)

    # Axis Settings
    ax.set_xlim(ax_limits[0], ax_limits[1])
    ax.set_ylim(ax_limits[2], ax_limits[3])
    ax.set_xlabel('X Coordinate (meters)')
    ax.set_ylabel('Y Coordinate (meters)')
    ax.grid(linestyle='--', alpha=0.7)

    # Legend processing
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = dict(zip(labels, handles))
    ax.legend(unique_labels.values(), unique_labels.keys(), loc='upper right')

    return fig, ax


if __name__ == "__main__":
    fig, ax = plot_warehouse_layout()
    plt.show()
