#!/bin/sh
### Launch the code for the times t1-t2 and using 5 cores
### and save the magnitude of the projected violating triangles \Delta_v at the level of edges
### on the file "edges_projection.hd5"
codepath="../High_order_TS/simplicial_multivariate.py"
filename="./../input/subject1_left.txt"
weighted_network="./../output/sub1_left_weighted"
result_file="./../output/subject1_left_results.txt"

python ${codepath} ${filename} -t 0 1200 -p 12 -s ${weighted_network} > ${result_file}
