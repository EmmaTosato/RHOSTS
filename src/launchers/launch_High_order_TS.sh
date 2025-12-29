#!/bin/sh
### Launch the code for the times t1-t2 and using 5 cores
codepath="../high_order_ts/simplicial_multivariate.py"
filename="./../input/subject1_left.txt"
weighted_network="./../output/sub1_left_weighted"
result_file="./../output/subject1_left_results.txt"

python ${codepath} ${filename} -t 0 5 -p 5 > ${result_file}
