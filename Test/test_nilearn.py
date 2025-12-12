import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from nilearn import plotting, datasets

try:
    print("Fetching fsaverage...")
    fsaverage = datasets.fetch_surf_fsaverage()
    print("Plotting surface...")
    fig = plotting.plot_surf(fsaverage.infl_left, fsaverage.sulc_left, hemi='left',
                       title='Surface plot', output_file='test_nilearn.png')
    print("Plot generated successfully.")
except Exception as e:
    print(f"Nilearn plot failed: {e}")
