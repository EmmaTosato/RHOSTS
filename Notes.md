# Notes

## Example folder
`.sh` files for running different scripts
- `High_order_TS` implement the algorithms to compute the global/local **higher-order indicators** from a multivariate time series  
- `High_order_TS_with_scaffold` implement the algorithms to compute the **homological scaffold** from multivariate time series

## High order TS
The main goal is to compute the higher-order indicators (hyper-coherence and hyper-complexity)

1. Usage of the `Pool` class from Python’s `multiprocessing` module that allows to run multiple function calls in parallel across different CPU cores
   - Each worker process must have access to the simplicial framework
   - By initializing `ts_simplicial` once per worker, we avoid recomputing the entire structure multiple times, saving computational resources
   
2. `create_simplicial_framework_from_data` --> `simplicial_complex_mvts`
   - Initializes a higher-order representation of the data.
   - For each time point $t$ a weighted simplicial complex is constructed

