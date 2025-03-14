# Notes

## Example folder
`.sh` files for running different scripts
- `High_order_TS` implement the algorithms to compute the global/local **higher-order indicators** from a multivariate time series  
- `High_order_TS_with_scaffold` implement the algorithms to compute the **homological scaffold** from multivariate time series

## High order TS
The main goal is to compute the higher-order indicators (hyper-coherence and hyper-complexity)

1. Usage of the `Pool` class from Python’s `multiprocessing` module that allows to run multiple function calls in parallel across different CPU cores
- A pool of worker processes is thus created
- Each worker process runs `create_simplicial_framework_from_data()` 
- This sets up the necessary data structure (`ts_simplicial`) before processing individual time steps.
- Using `initializer`, we have that each worker initializes its own copy of the `ts_simplicial` object (=each worker has a separate instance).

2. `create_simplicial_framework_from_data()`
- `ts_simplicial` is global because each worker has the same initialized simplicial framework to avoid redundant computations.
- `simplicial_complex_mvts` is called

3. The `simplicial_complex_mvts` class constructs the higher-order structure of the multivariate time series
- Initialization
- Z-score normalization
- Shuffling for Null Model (if enabled)
- `compute_edges_triplets` precomputes edges and triplets to speed up later computations:
  - Computation of edges**:
    - For each pair (i, j), the element-wise product between their respective signals across time is computed --> this captures their instantaneous co-fluctuation
    - Statistical properties (like mean and std deviation) of the time series are stored, and they we'll be re-used by the later computations
    - Edges' instantaneous co-fluctuations are z-scored again to ensure comparability across all the edge time series (1-Order Co-Fluctuations)
  - Computation for triplets (triangles): same


3. For each time t, `launch_code_one_t` is run:
- `create_simplicial_complex`: weighted simplicial complex from a multivariate time series at a specific time step
  - Add **Nodes** (0-Simplices)
    - Nodes Always Exist Before Higher-Order Structures (edges, triplets in this case) --> Proper Filtration Order
    - By assigning the maximum weight to all nodes, we ensure that nodes appear first in the filtration sequence.
    - This allow Persistent Homology to work properly and prevents topological violations
  - Adding **Edges** (1-Simplices)
    - Loops over precomputed edges and retrieves values
    - Computes the z-scored weight for this edge at time t --> This tells us how strong the co-fluctuation is compared to the historical average
    - Adjusts the weight sign based on coherence
      - *Positive*: if an edge or triplet has fully synchronized signals (coherence = 1), it is assigned a positive weight.
      - *Negative*: if an edge or triplet are mixed (decorrelated or incoherent, coherence ≠ 1), it gets a negative weight.
      - The edge is added to the simplicial complex
  - Adding **Triplets** (2-Simplices)
    - Same pipeline
- Filtering Invalid Simplices with `fix_violations`:
  - Ensure simplicial closure
  - Identify and remove "violating" simplices (triplets with higher coherence than their edges)
  - Measure how many triangles were discarded
- Computing the Persistence Diagram
  - This extracts topological features (connected components, loops, cavities) from the simplicial complex at a time point
  - Output `dgms1` is an array of (First column → Birth time, Second column → Death time) pairs, where each row represents a topological feature (H0, H1 and H2).
  - Birth:
    - Negative birth values --> Features that appear in a fully coherent regime.
    - Positive birth values --> Features that emerge in a fully decoherent regime.
  - Death:
    - Negative death values --> Features that disappear within the coherent phase.
    - Positive death values --> Features that persist into decoherent. 
    - Some features in dgms1 might have inf as their death time (they never disappear).
    >NB: When we compute persistent homology, birth and death times are flipped in sign respect to sign og the weight of edges and triplets 
- Handling Infinite Filtration Values
- Computing the Hyper-Complexity Indicator: 
  - Uses Wasserstein distance to measure topological complexity.
- Extracting Different Types of Topological Features: Identifies coherent and decoherent structures.
  - Fully Coherent Features
  - Coherent Transition Features
  - Fully Decoherent Features
- Computing Wasserstein Distances for Each Type of features --> quantitative measure of complexity
- Computing the Average Edge Violation: counts how many edges fail to support triplets
  - Higher avg_edge_violation → Many triangles violate simplicial closure → In high avg_edge_violation systems, group behaviors emerge unpredictably, meaning higher-order effects dominate.
  - Lower avg_edge_violation → Pairwise relationships are sufficient to explain triplets.
- Computing the Edge Weights from Violating Triplets
- Returning Results
  - *Time step*: The index of the current time point being analyzed.
  - **Overall topological complexity**
  - **Fully Coherent Complexity**: Measures coherent structures (features that appear and disappear in a synchronized state). Higher values mean more persistent synchronization.
  - **Coherent Transition Complexity**: Features that start in a synchronized phase but disappear in a chaotic phase. High values indicate phase transitions.
  - **Fully Decoherent Complexity**: Features that exist only in a chaotic phase. Higher values mean more randomness.
  - **Hyper-coherence** (degree of simplicial violations): Measures how often higher-order interactions do not follow expected pairwise relationships. Values near 1 indicate dominant higher-order effects.
  - **Average edge violation**:Tracks how frequently edges fail to predict triplet interactions. High values indicate inconsistencies in simplicial structure. 
  - **Weighted representation of violations**: A dictionary mapping edges to weights, representing how much they contribute to simplicial violations. This allows tracking of which edges are most responsible for inconsistencies.

> For Each Time Point, We Have a Topological Description of the Time Series at That Moment.
> We move beyond raw time series and capture higher-order interactions.
