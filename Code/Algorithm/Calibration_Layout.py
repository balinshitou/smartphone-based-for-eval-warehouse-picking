import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def draw_segment_length(ax, p1, p2, offset=0.25, text_offset=-0.2, color='#333333'):
    x1, y1 = p1
    x2, y2 = p2

    if y1 == y2:
        y = y1 + offset

        ax.plot([x1, x1], [y1, y], color=color, linestyle="--", lw=1.2)
        ax.plot([x2, x2], [y2, y], color=color, linestyle="--", lw=1.2)

        ax.annotate(
            '',
            xy=(x2, y - offset / 2),
            xytext=(x1, y - offset / 2),
            arrowprops=dict(arrowstyle='<->', color=color, lw=1.2)
        )

        length = abs(x2 - x1)

        ax.text(
            (x1 + x2) / 2, y + text_offset,
            f'{length:.1f} m',
            ha='center',
            va='bottom',
            fontsize=10,
            bbox=dict(facecolor='white', edgecolor='none', pad=1.2)
        )

    elif x1 == x2:
        x = x1 + offset

        ax.plot([x1, x], [y1, y1], color=color, linestyle="--", lw=1.2)
        ax.plot([x2, x], [y2, y2], color=color, linestyle="--", lw=1.2)

        ax.annotate(
            '',
            xy=(x, y2),
            xytext=(x, y1),
            arrowprops=dict(arrowstyle='<->', color=color, lw=1.2)
        )

        length = abs(y2 - y1)

        ax.text(
            x + text_offset - 0.1, (y1 + y2) / 2,
            f'{length:.1f} m',
            ha='left',
            va='center',
            fontsize=10,
            bbox=dict(facecolor='white', edgecolor='none', pad=1.2)
        )


shelf_color = '#7f7f7f'
path_color = '#1f77b4'
point_color = '#d62728'
text_color = '#333333'


def Cablibration_Path():
    fig, ax = plt.subplots(figsize=(8, 8))
    # "Arial" or  "Helvetica"
    plt.rcParams['font.family'] = 'Arial'

    # warehouse dimensions
    warehouse_length = 7.25
    warehouse_width = 6.9

    # shelf layout
    shelves = [
        (0.2, 0.1, 1.9, 0.6), (2.1, 0.1, 1.9, 0.6),
        (4, 0.7, 0.6, 1.9), (4, 2.6, 0.6, 1.9), (4, 4.5, 0.6, 1.9),
        (1.65, 6.4, 1.9, 0.6), (-0.25, 6.4, 1.9, 0.6),
        (-0.85, 4.5, 0.6, 1.9), (-0.85, 2.6, 0.6, 1.9),
        (-2.65, 1.3, 0.6, 1.9)
    ]

    for (x, y, w, h) in shelves:
        rect = plt.Rectangle(
            (x, y), w, h,
            edgecolor=shelf_color,
            facecolor='none',
            lw=1.5,
            hatch="///"
        )
        ax.add_patch(rect)

    ax.scatter(-1.85, 0, color='black', s=60, zorder=3)
    ax.scatter(0, 0, color='black', s=60, zorder=3)

    ax.text(-3.35, -0.05, "Outbound Point", fontsize=11, color=text_color)
    ax.text(-0.4, -0.25, "Inbound Point", fontsize=11, color=text_color)

    # Picking Points
    points = {'A': (4, 3.55), 'B': (0.75, 6.4), 'C': (-2.05, 2.4)}

    for label, (x, y) in points.items():
        ax.scatter(
            x, y,
            color=point_color,
            s=80,
            edgecolor='white',
            linewidth=1.5,
            zorder=4
        )

        ax.text(
            x + 0.15, y + 0.15, label,
            fontsize=14,
            weight='bold',
            color=point_color,
            bbox=dict(facecolor='none', edgecolor='none', alpha=0.7)
        )

    # Picking Path
    path = [
        (0, 0), (0, 0.9), (3.8, 0.9), (3.8, 6.2),
        (-0.05, 6.2), (-0.05, 2.4), (-1.85, 2.4), (-1.85, 0)
    ]

    draw_segment_length(ax, path[1], path[2])
    draw_segment_length(ax, path[2], path[3], offset=-0.15, text_offset=-0.15)
    draw_segment_length(ax, path[3], path[4], offset=-0.25, text_offset=0.03)
    draw_segment_length(ax, path[4], path[5], offset=0.15, text_offset=0)
    draw_segment_length(ax, path[5], path[6], offset=-0.25, text_offset=0.05)
    draw_segment_length(ax, path[6], path[7], offset=0.15, text_offset=0)

    path_x, path_y = zip(*path)

    ax.plot(
        path_x, path_y,
        color=path_color,
        lw=2.8,
        label='Picking Path'
    )

    arrows = [
        (0, 0, 0, 0.6),
        (2.1, 0.9, 0.6, 0),
        (3.8, 2, 0, 0.6),
        (3, 6.2, -0.6, 0),
        (-0.05, 5, 0, -0.6),
        (-1.85, 0, 0, -0.6)
    ]

    for x, y, dx, dy in arrows:
        ax.arrow(
            x, y, dx, dy,
            head_width=0.18,
            head_length=0.18,
            fc=path_color,
            ec=path_color,
            length_includes_head=True
        )

    # Length and Width annotation
    y_pos = -1
    gap_x = 0.8

    left = -2.8
    right = 4.6
    mid = (left + right) / 2

    ax.annotate(
        '',
        xy=(mid - gap_x / 2, y_pos),
        xytext=(left, y_pos),
        arrowprops=dict(arrowstyle='<-', color=text_color)
    )

    ax.annotate(
        '',
        xy=(right, y_pos),
        xytext=(mid + gap_x / 2, y_pos),
        arrowprops=dict(arrowstyle='->', color=text_color)
    )

    ax.text(
        mid, y_pos,
        f'{warehouse_length} m',
        ha='center',
        va='center',
        fontsize=11,
        bbox=dict(facecolor='white', edgecolor='none', pad=1.5)
    )

    # Width
    x_pos = 5.1
    gap_y = 0.4

    bottom = 0
    top = 7
    mid = (bottom + top) / 2

    ax.annotate(
        '',
        xy=(x_pos, mid - gap_y / 2),
        xytext=(x_pos, bottom),
        arrowprops=dict(arrowstyle='<-', color=text_color)
    )

    ax.annotate(
        '',
        xy=(x_pos, top),
        xytext=(x_pos, mid + gap_y / 2),
        arrowprops=dict(arrowstyle='->', color=text_color)
    )

    ax.text(
        x_pos, mid,
        f'{warehouse_width} m',
        ha='center',
        va='center',
        fontsize=11,
        bbox=dict(facecolor='white', edgecolor='none', pad=1.5)
    )

    ax.set_aspect('equal')
    ax.set_xlim(-3.5, 6)
    ax.set_ylim(-1.5, 8)

    path_handle = plt.Line2D([0], [0], color=path_color, lw=2, label='Calibration Path')
    shelf_handle = mpatches.Patch(facecolor='none', edgecolor=shelf_color, hatch='///', label='Shelf')
    point_handle = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=point_color, markersize=8,
                              label='Picking point')
    # "upper left"
    ax.legend(handles=[path_handle, shelf_handle, point_handle], loc="upper left", fontsize=12, frameon=False)

    # border_setting "top"/"right"/"left"/"bottom"
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    plt.tight_layout()
    # plt.savefig("Parameter_Setting.svg", dpi=300)
    # plt.savefig("Parameter_Setting.png", dpi=300)
    plt.show()


Cablibration_Path()
