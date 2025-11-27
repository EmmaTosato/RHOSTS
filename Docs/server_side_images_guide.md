# Server-Side Image Generation Guide

## Problem
The cluster compute nodes lack an X server, which VTK requires for rendering brain maps even when saving to files.

## Solution 1: Request xvfb Installation (Recommended)

Ask your system administrator to install `xvfb` (X Virtual Framebuffer) on the compute nodes:

```bash
# Admin command (requires sudo)
sudo apt-get install xvfb
```

Once installed, you can enable image generation in `main.sh`:

```bash
# Enable server-side image generation
GENERATE_IMAGES=true sbatch src/higher_order/main.sh
```

The script will automatically use `xvfb-run` if available.

## Solution 2: Manual xvfb Wrapper (If xvfb is installed)

If xvfb is available but you want more control:

```bash
# Modify the python call in main.sh to:
xvfb-run -a python -m src.higher_order.main "${args[@]}"
```

## Solution 3: Local Generation (Current Default)

Generate `.npy` files on the server, download them, and create images locally:

```bash
# On cluster (default, GENERATE_IMAGES=false)
sbatch src/higher_order/main.sh

# Download .npy files to your PC
scp -r user@cluster:/data/etosato/RHOSTS/Output/lorenzo_data/node_strengths/dv/ ./local_data/

# Generate images locally
python src/higher_order/batch_generate_images.py local_data/ local_images/
```

See `local_visualization_guide.md` for detailed local workflow instructions.

## Alternative Libraries (Not Recommended)

Other rendering libraries have similar X server requirements:
- **Mayavi**: Also requires X server or xvfb
- **PyVista with OSMesa**: Requires complex VTK recompilation
- **Plotly**: Different visualization style, would require rewriting `normal_view`

The current VTK/surfplot stack is optimal for neuroimaging; **xvfb is the practical solution**.
