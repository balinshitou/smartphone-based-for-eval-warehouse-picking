import sys
import matplotlib.pyplot as plt
from pathlib import Path

'''
Automated execution pipeline for PDR algorithm and trajectory reconstruction.
'''

# ==========================================
# 1. Configure Automated Plot Saving
# ==========================================
# Define the output directory for all generated plots
OUTPUT_DIR = Path("./Output_Figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
figure_count = 1


def save_and_close_plot(*args, **kwargs):
    """
    Override standard plt.show() to save the figure locally
    without blocking the continuous execution of the scripts.
    """
    global figure_count
    fig = plt.gcf()
    if fig.get_axes():  # Ensure the figure actually contains data
        save_path = OUTPUT_DIR / f"PDR_Visualization_{figure_count}.png"
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"  -> [Visualization Saved] {save_path.resolve()}")
        figure_count += 1
    plt.close(fig)  # Close to prevent memory leaks and UI blocking


# Apply the override dynamically (Monkey-patching)
plt.show = save_and_close_plot

# ==========================================
# 2. Import Modules
# ==========================================
try:
    import Acc_Comparison
    import Parameter_Configuration
    import Path_Comparison
    import PDR_Trajectory
    import Final_Score
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Please ensure all scripts are in the same directory.")
    sys.exit(1)


# ==========================================
# 3. Main Execution Pipeline
# ==========================================
def main():
    print("=" * 60)
    print("🚀 Starting PDR Automated Pipeline".center(60))
    print("=" * 60)

    try:
        # Step 1: Acceleration Filtering Comparison
        print("\n>>> Stage 1: Running Acc_Comparison <<<")
        Acc_Comparison.main()

        # Step 2: Kalman Filter Grid Search
        print("\n>>> Stage 2: Running Parameter_Configuration <<<")
        # Utilizing the default parameters from your original script's __main__ block
        test_path = './Dataset/KF_Param_Tuning'
        Parameter_Configuration.optimize_kalman_qr_params(data_dir=test_path, true_distance_val=21.85)

        # Step 3: Multi-stage Path Comparison
        print("\n>>> Stage 3: Running Path_Comparison <<<")
        Path_Comparison.main()

        # Step 4: Single PDR Trajectory Reconstruction
        print("\n>>> Stage 4: Running PDR_Trajectory <<<")
        PDR_Trajectory.main()

        # Step 5: Final Evaluation Metrics & Statistical Tables
        print("\n>>> Stage 5: Running Final_Score (Metrics Evaluation) <<<")
        Final_Score.main()

    except Exception as e:
        print(f"\n❌ Pipeline interrupted due to an error: {e}")
        sys.exit(1)

    # ==========================================
    # 4. Final Status Report
    # ==========================================
    print("\n" + "=" * 60)
    print("✅ Pipeline Execution Completed Successfully!".center(60))
    print("-" * 60)
    print("All required scripts have been executed.")
    print(f"All generated visualizations are saved in:\n📂 {OUTPUT_DIR.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
