# High-frequency trading in a limit order book

**Paper:** Marco Avellaneda & Sasha Stoikov, "High-frequency trading in a limit order book" (2008)

This repository reproduces the numerical simulations from Section 3.3 of the paper:
the inventory-based market-making strategy derived via approximate closed-form solutions
(equations 3.17–3.18) and its Monte Carlo comparison against a symmetric benchmark.

## Experiments

| Experiment | Description | Paper reference |
|------------|-------------|-----------------|
| `exp1` | Single-path simulation (γ=0.1); qualitative Figure 1 | Section 3.3, Figure 1 |
| `exp2` | 1 000-path Monte Carlo comparison, γ=0.1 | Section 3.3, Table 1 |
| `exp3` | 1 000-path Monte Carlo comparison, γ=0.01 | Section 3.3, Table 2 |
| `exp4` | 1 000-path Monte Carlo comparison, γ=0.5 | Section 3.3, Table 3 |

## Setup

```bash
pip install -r requirements.txt
```

No API keys are required. All experiments use synthetic data generated internally.

## Running experiments

```bash
# Single-path illustration (Figure 1 analogue)
python -m exp.exp1

# Monte Carlo comparison, gamma = 0.1 (Table 1)
python -m exp.exp2

# Monte Carlo comparison, gamma = 0.01 (Table 2)
python -m exp.exp3

# Monte Carlo comparison, gamma = 0.5 (Table 3)
python -m exp.exp4
```

## Running tests

```bash
python -m pytest -m "not market_data"
```

## Reproduce all at once

```bash
bash reproduce.sh
```

## Parameters

All simulation parameters are stored in `src/config.py`. Key values from Section 3.3:

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `S0` | 100 | Initial mid-price |
| `T` | 1 | Trading horizon |
| `SIGMA` | 2 | Mid-price volatility σ |
| `DT` | 0.005 | Time step dt |
| `K` | 1.5 | Order-arrival decay rate k |
| `A` | 140 | Base order-arrival intensity A |
| `N_PATHS` | 1 000 | Monte Carlo paths |

## Results

Results are written to `results/`:
- `exp1_figure1.png` – single-path quote/price plot (Figure 1 analogue)
- `exp1_path.csv` – per-step time series for the single path
- `exp2_table.csv`, `exp3_table.csv`, `exp4_table.csv` – summary statistics
- `exp2_histogram.png`, `exp3_histogram.png`, `exp4_histogram.png` – P&L histograms

See `results/RESULTS.md` for a comparison against the paper's tables.

## Repository layout

```
.
├── README.md
├── AGENTS.md
├── reproduce.sh
├── requirements.txt
├── .env.example
├── src/
│   ├── config.py         # All parameters (Section 3.3)
│   └── simulator.py      # AvellanedaStoikovSimulator, quote functions
├── exp/
│   ├── exp1.py           # Single-path simulation
│   ├── exp2.py           # MC comparison, γ=0.1
│   ├── exp3.py           # MC comparison, γ=0.01
│   └── exp4.py           # MC comparison, γ=0.5
├── data/
│   └── generate_synthetic.py  # Synthetic path generator
├── tests/
│   ├── conftest.py
│   └── test_simulator.py
└── results/
    └── RESULTS.md
```
