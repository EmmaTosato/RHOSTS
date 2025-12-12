import os
import sys
import numpy as np

# Mock arguments
class Args:
    metric = "coherence"
    output_img = "test_fallback_image.png"

args = Args()
nodal = np.random.rand(100) # Mock 100 ROI values
cmap = "RdBu_r"

# Force headless environment
if "DISPLAY" in os.environ:
    del os.environ["DISPLAY"]

print("Simulating headless environment (DISPLAY unset).")

try:
    print("Attempting to import and use nilearn_view...")
    # Add project root to path
    sys.path.append("/data/etosato/RHOSTS")
    from src.higher_order.visualization.utils_nilearn_brain import nilearn_view
    
    fig = nilearn_view(
        current_nodestrength=nodal,
        cmap=cmap,
        title=f"Brain Map (Nilearn) - {args.metric}"
    )
    
    if fig:
        fig.savefig(args.output_img)
        print(f"Successfully saved {args.output_img}")
    else:
        print("Error: nilearn_view returned None")

except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
