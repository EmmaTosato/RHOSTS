#!/bin/sh
### Launch the code for the times 0-5 and using 5 cores 
### and save the magnitude of the projected violating triangles \Delta_v at the level of edges
### on the file "edges_projection.hd5"
codepath="../High_order_TS/simplicial_multivariate.py"
filename="./../Kaneko_CLM/subject1_left.txt"
outputfile_edges="../Sample_results/edges_projection_sub1_left_1200"
outputfile="../Sample_results/results_sub1_left_1200.txt"

python ${codepath} ${filename} -t 0 1200 -p 5 -s ${outputfile_edges} > ${outputfile}