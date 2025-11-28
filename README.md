# Local Visualization Guide

Since the cluster cannot generate images due to missing X server support, you can generate them locally on your PC.

## Prerequisites

On your local machine, install the required packages:

```bash
pip install matplotlib numpy surfplot neuromaps brainspace
```

## Step 1: Download .npy Files from Cluster

Use `scp` or your preferred method to download the generated `.npy` files:

```bash
# Download single file
scp user@cluster:/data/etosato/RHOSTS/Output/lorenzo_data/node_strengths/dv/134829_all_frames.npy ./

# Download entire directory
scp -r user@cluster:/data/etosato/RHOSTS/Output/lorenzo_data/node_strengths/dv/ ./local_data/
```

## Step 2: Generate Images Locally

### Option A: Single Image

```bash
python src/higher_order/generate_images_local.py \
    local_data/134829_all_frames.npy \
    local_images/134829_all_frames.png
```

### Option B: Batch Processing

Generate images for all `.npy` files in a directory:

```bash
python src/higher_order/batch_generate_images.py \
    local_data/ \
    local_images/
```

### Custom Colormap

You can specify a different colormap:

```bash
python src/higher_order/generate_images_local.py \
    local_data/134829_all_frames.npy \
    local_images/134829_all_frames.png \
    RdBu_r
```

Available colormaps:
- `green_yellow_red` (default)
- `RdBu_r`
- `custom`

## Alternative: Server-Side Solutions

If you need images generated on the cluster, contact the system administrator to:

1. **Install xvfb**: This virtual framebuffer allows headless rendering
   ```bash
   # Admin installs on compute nodes
   sudo apt-get install xvfb
   ```

2. **Modify main.sh** to use xvfb-run:
   ```bash
   xvfb-run python -m src.higher_order.main ...
   ```

This would enable the pipeline to generate images directly on the cluster without manual intervention.
