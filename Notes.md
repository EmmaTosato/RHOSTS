# Notes

## Example folder
`.sh` files for running different scripts
- `High_order_TS` implement the algorithms to compute the global/local **higher-order indicators** from a multivariate time series  
- `High_order_TS_with_scaffold` implement the algorithms to compute the **homological scaffold** from multivariate time series

## High order TS
The main goal is to compute the higher-order indicators (hyper-coherence and hyper-complexity)

1. Usage of the `Pool` class from Python’s `multiprocessing` module that allows to run multiple function calls in parallel across different CPU cores
- Each parallel worker process initializes a shared simplicial complex object
- By initializing `ts_simplicial` once per worker, we avoid recomputing the entire structure multiple times, saving computational resources
   
2. With `create_simplicial_framework_from_data` and `simplicial_complex_mvts`a multivariate time series data is translated into a weighted simplicial complex (the structure containing all the edges and triplets (triangles)). Thus a weighted simplicial complex for each time point, resulting in a sequence of them
     - **Initialization**
     - **Z-score normalization**
     - **Computation of edges**:
       - For each pair (i, j), the element-wise product between their respective signals across time is computed. This captures their instantaneous co-fluctuation
       - Edges' instantaneous co-fluctuations are z-scored again to ensure comparability across all the edge time series (1-Order Co-Fluctuations)
     - **Computation for triplets (triangles)**: same
     - 
     
   