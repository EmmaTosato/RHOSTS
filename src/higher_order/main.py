import argparse
import numpy as np
from ..builders.dv_brainmap import compute_brainmap_dv
from ..builders.scaffold_brainmap import compute_brainmap_scaffold

def parse_args():
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

    # Nuovi: metric e direction per gestire hyper vs complexity, high vs low
    p.add_argument(
        "--metric",
        choices=["hyper", "complexity"],
        default="hyper",
        help="Metric column in txt: 'hyper' (col 5) or 'complexity' (col 1).",
    )
    p.add_argument(
        "--direction",
        choices=["high", "low"],
        default="high",
        help="'high' = top percent, 'low' = bottom percent.",
    )

    p.add_argument("--output-npy", required=True)
    return p.parse_args()


def main():
    args = parse_args()

    if args.mode == "dv":
        nodal = compute_brainmap_dv(
            hd5_paths=args.inputs,
            scenario=args.scenario,
            frame=args.frame,
            percent=args.percent,
            sorted_output_txt=args.sorted_output_txt,
            num_ROIs=args.num_rois,
            metric=args.metric,
            direction=args.direction,
        )
    else:
        nodal = compute_brainmap_scaffold(
            scaffold_directories=args.inputs,
            scenario=args.scenario,
            frame=args.frame,
            percent=args.percent,
            sorted_output_txt=args.sorted_output_txt,
            num_ROIs=args.num_rois,
            metric=args.metric,
            direction=args.direction,
        )

    np.save(args.output_npy, nodal)
    print("Saved to", args.output_npy)


if __name__ == "__main__":
    main()
