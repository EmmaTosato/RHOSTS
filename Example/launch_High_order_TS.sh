#!/bin/sh
# Launch the code for the times 0–100 using 5 cores
codepath="../High_order_TS/simplicial_multivariate.py"
filename="./../input/subject1_left.txt"
weighted_network="./../output/sub1_left_weighted"
result_file="./../output/subject1_left_results.txt"

python ${codepath} ${filename} -t 0 5 -p 5 -s ${weighted_network} > ${result_file}
