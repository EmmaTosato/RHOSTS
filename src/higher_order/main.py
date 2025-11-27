"""Command-line entry point for higher-order nodal strength computation."""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from .maps.brain_map import compute_brainmap_dv, compute_brainmap_scaffold
from .utils_neuromaps_brain import normal_view

def parse_args():
    """Define and parse CLI arguments for the brain map utilities."""
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["dv", "scaffold"], required=True)
    p.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="hd5 files (dv mode) OR scaffold folders (scaffold mode)",
    )
    p.add_argument(
        "--scenario",
        choices=["single_frame", "all_frames", "top_percent"],
        default="single_frame",
    )
    p.add_argument("--frame", type=int)
    p.add_argument("--percent", type=float, default=0.15)
    p.add_argument("--sorted-output-txt", type=str)
    p.add_argument("--num-rois", type=int, default=100)

    # Metric determines the sorting column and direction
    # coherence -> hyper-coherence (high values)
    # complexity -> complexity (low values)
    p.add_argument(
        "--metric",
        choices=["coherence", "complexity"],
        default="coherence",
        help="Metric for top_percent: 'coherence' (high) or 'complexity' (low).",
    )

    p.add_argument("--output-npy", required=True)
    p.add_argument("--output-img", help="Path to save the brain map image (optional)")
    return p.parse_args()


def main():
    """Dispatch to DV or scaffold pipeline and persist the resulting array."""
    args = parse_args()

    # Infer internal metric name and direction
    if args.metric == "coherence":
        internal_metric = "hyper"
        direction = "high"
    else:  # complexity
        internal_metric = "complexity"
        direction = "low"

    # Choose the correct computation based on the input modality
    if args.mode == "dv":
        nodal = compute_brainmap_dv(
            hd5_paths=args.inputs,
            scenario=args.scenario,
            frame=args.frame,
            percent=args.percent,
            sorted_output_txt=args.sorted_output_txt,
            num_ROIs=args.num_rois,
            metric=internal_metric,
            direction=direction,
        )
    else:
        nodal = compute_brainmap_scaffold(
            scaffold_directories=args.inputs,
            scenario=args.scenario,
            frame=args.frame,
            percent=args.percent,
            sorted_output_txt=args.sorted_output_txt,
            num_ROIs=args.num_rois,
            metric=internal_metric,
            direction=direction,
        )

    # Persist the numpy array for downstream analysis or visualization
    np.save(args.output_npy, nodal)
    print(f"Saved array to {args.output_npy}")

    # Generate and save visualization if requested
    if args.output_img:
        # Define colormap as in the notebook
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "green_yellow_red", ["#2ca25f", "#ffffbf", "#d73027"]
        )
        
        # Generate the view
        # Note: normal_view returns a figure
        fig = normal_view(
            current_nodestrength=nodal,
            edges=True,
            cmap=cmap,
            q_thresh=0.0,
            center_cbar=True,
            alpha_graymap=0.99,
            xlabel=r"$\langle s_i \rangle$"
        )
        
        # Save the figure
        fig.savefig(args.output_img, dpi=300, bbox_inches="tight")
        print(f"Saved image to {args.output_img}")
        plt.close(fig)


if __name__ == "__main__":
    main()
