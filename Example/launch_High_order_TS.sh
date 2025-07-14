#!/bin/sh
### Launch the code for the times 0-5 and using 5 cores
codepath="../High_order_TS/simplicial_multivariate.py"
filename="./../input/subject1_left.txt"
weighted_network="./../output/sub1_left_weighted"

python ${codepath} ${filename} -t 0 1200 -p 5 -s ${weighted_network}


