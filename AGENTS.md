# AGENTS.md — Avellaneda-Stoikov replication

## What this repository implements

Replication of the numerical experiments in Section 3.3 of:

> Marco Avellaneda & Sasha Stoikov, "High-frequency trading in a limit order book" (2008)

The repository implements the approximate finite-horizon market-making strategy
(equations 3.17–3.18) and reproduces Tables 1–3 and the qualitative behaviour
of Figures 1–4.

## Layout

```
.
├── README.md
├── AGENTS.md               ← this file
├── reproduce.sh            ← runs all tests and experiments
├── requirements.txt
├── .env.example            ← placeholder (no API keys needed)
├── src/
│   ├── __init__.py
│   ├── config.py           ← ALL experiment parameters (Section 3.3)
│   └── simulator.py        ← AvellanedaStoikovSimulator, quote functions
├── exp/
│   ├── __init__.py
│   ├── exp1.py             ← single-path simulation (Figure 1 analogue)
│   ├── exp2.py             ← 1 000-path MC comparison, γ=0.1  (Table 1)
│   ├── exp3.py             ← 1 000-path MC comparison, γ=0.01 (Table 2)
│   └── exp4.py             ← 1 000-path MC comparison, γ=0.5  (Table 3)
├── data/
│   ├── __init__.py
│   └── generate_synthetic.py   ← synthetic path generator; no real market data
├── tests/
│   ├── conftest.py
│   └── test_simulator.py
└── results/
    ├── RESULTS.md
    ├── exp1_figure1.png
    ├── exp1_path.csv
    ├── exp1_figure1_table.csv
    ├── exp2_table.csv
    ├── exp2_histogram.png
    ├── exp3_table.csv
    ├── exp3_histogram.png
    ├── exp4_table.csv
    └── exp4_histogram.png
```

## Setup

```bash
pip install -r requirements.txt
```

No API keys are required; all experiments use internally generated synthetic data.

## Running tests

```bash
python -m pytest -m "not market_data"   # standard suite (no live API)
python -m pytest                         # full suite (identical here)
```

## Running experiments

```bash
python -m exp.exp1    # single path (Figure 1 analogue)
python -m exp.exp2    # MC comparison γ=0.1  (Table 1)
python -m exp.exp3    # MC comparison γ=0.01 (Table 2)
python -m exp.exp4    # MC comparison γ=0.5  (Table 3)
```

Or run everything at once:

```bash
bash reproduce.sh
```

## Paper configuration

The full paper configuration is already implemented (1 000 paths, all three
γ values, dt = 0.005, T = 1).  No `--full` flag is needed; the experiments
already run the paper's configuration.

## Conventions

- **All experiment parameters** live in `src/config.py` as module-level
  `UPPER_CASE` variables with comments giving meaning, unit, and paper reference.
- **Data generation** is exclusively in `data/generate_synthetic.py`; no
  loader or generator lives in `src/` or `exp/`.
- **Test files** live entirely in `tests/`; they import from `src/` and
  `data/` via the module path `python -m pytest` sets up automatically.
- **No sys.path edits** appear anywhere; run from the repository root.
- **Result files** are written to `results/` (CSV and PNG).  After a rerun,
  the CSV and PNG files are overwritten; the numbers and verdicts in
  `results/RESULTS.md` must be checked against the new files and updated by hand.
- **API keys**: none are used.  `.env.example` holds empty placeholders only.
- **Secrets**: never commit `.env` or any file containing credentials.
