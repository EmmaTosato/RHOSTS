# Guide for launching Jupyter

## 1. Starting Jupyter on the server (via SLURM)

On the login node:

```
cd /data/etosato/RHOSTS/Notebooks
sbatch run_jupyter.sbatch
```

Check the job:

```
squeue -u etosato
```

Note the `JOBID` (e.g., `143541`).

---

## 2. Connecting from the Mac

With VPN active:

```
/Users/emmatosato/Documents/PhD/Projects/connect_jupyter.sh <JOBID>
```

Or:

```
/Users/emmatosato/Documents/PhD/Projects/connect_jupyter.sh latest
```

The script:

* automatically reads the node, port, and token from the SLURM log,
* opens the SSH tunnel,
* prints the local URL to open in the browser.

Example output:

```
NODE=brain02  PORT=52217
Local port: 9999
URL: http://localhost:9999/lab?token=...
```

Open the URL in your browser.

---

## 3. Closing the session

When finished:

* On the Mac: close the tunnel with `Ctrl + C`
* On the server: terminate the job with

```
scancel <JOBID>
```

