# Job Scheduling Simulator

## What this project does
Interactive single-machine job scheduling using:
- FCFS — First Come, First Served
- SPT — Shortest Processing Time
- EDD — Earliest Due Date
- Priority — 1 = highest priority

## Inputs
- Job
- Arrival time (decimal hours)
- Processing time (hours)
- Due time (decimal hours)
- Priority

## Outputs
- Start time
- Completion time
- Waiting time
- Flow time
- Lateness
- Delay / Tardiness
- Earliness
- On-time %
- Machine utilisation
- Makespan
- Comparison dashboard
- Machine timeline / Gantt-style chart

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows:

```bash
.venv\Scripts\activate
python -m streamlit run app.py
```

## GitHub
Do NOT commit `.venv/`. Add this to `.gitignore`:

```
.venv/
__pycache__/
*.pyc
.DS_Store
.streamlit/secrets.toml
```
