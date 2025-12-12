"""Command-line entry point for higher-order nodal strength computation."""

import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolorst
import matplotlib.colors as mcolors
from ..nodal_strength.pipeline import compute_brainmap_dv, compute_brainmap_scaffold
from ..visualization.utils_neuromaps_brain import normal_view

def parse_args():
    """Define and parse CLI arguments for the brain map utilities."""
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["dv", "scaffold", "group"], required=True)
    p.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="hd5 files (dv), scaffold folders (scaffold), or npy files (group)",
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
    """Dispatch to DV, scaffold, or group pipeline and persist the resulting array."""
    args = parse_args()

    # Infer internal metric name and direction
    if args.metric == "coherence":
        internal_metric = "hyper"
        direction = "high"
    else:  # complexity
        internal_metric = "complexity"
        direction = "low"

    # Choose the correct computation based on the input modality
    if args.mode == "group":
        # Group mode: inputs are .npy files to be averaged
        print(f"Running GROUP analysis on {len(args.inputs)} files.")
        arrays = []
        for f in args.inputs:
            try:
                arr = np.load(f)
                arrays.append(arr)
            except Exception as e:
                print(f"WARNING: Could not load {f}: {e}")
        
        if not arrays:
            print("ERROR: No valid arrays loaded.")
            exit(1)
            
        # Stack and average
        stack = np.vstack(arrays)
        nodal = np.mean(stack, axis=0)
        print(f"Computed group mean from {len(arrays)} inputs.")

    elif args.mode == "dv":
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
    else: # scaffold
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
        print(f"Attempting to generate image at {args.output_img}...")
        try:
            # Define colormap as in the notebook
            cmap = mcolors.LinearSegmentedColormap.from_list(
                "green_yellow_red", ["#2ca25f", "#ffffbf", "#d73027"]
            )
            
            # Generate the view
            import os
            fig = None
            if os.environ.get("DISPLAY") is None:
                print("WARNING: DISPLAY environment variable not set. Using nilearn fallback.")
                from ..visualization.utils_nilearn_brain import nilearn_view
                try:
                    fig = nilearn_view(
                        current_nodestrength=nodal,
                        cmap='RdBu_r',
                        title=f"Brain Map (Nilearn) - {args.metric}"
                    )
                except Exception as e:
                    print(f"ERROR: Nilearn fallback failed: {e}")
                    return
            else:
                # Use original surfplot method
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
            if fig is not None:
                fig.savefig(args.output_img, dpi=300, bbox_inches="tight")
                print(f"Saved image to {args.output_img}")
                plt.close(fig)
        except Exception as e:
            print(f"WARNING: Failed to generate image: {e}")
            print("Proceeding without image generation. This is likely due to missing X server (xvfb).")
            # Do not re-raise, just continue



if __name__ == "__main__":
    main()
