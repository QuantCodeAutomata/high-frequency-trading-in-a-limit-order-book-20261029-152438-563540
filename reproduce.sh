#!/usr/bin/env bash
# Reproduce all experiments for Avellaneda & Stoikov (2008).
set -u

echo "=== Installing dependencies ==="
pip install -q -r requirements.txt

echo ""
echo "=== Running tests ==="
python -m pytest -m "not market_data" -v

echo ""
echo "=== Experiment 1: single-path simulation (Figure 1 analogue) ==="
python -m exp.exp1

echo ""
echo "=== Experiment 2: Monte Carlo comparison, gamma=0.1 (Table 1) ==="
python -m exp.exp2

echo ""
echo "=== Experiment 3: Monte Carlo comparison, gamma=0.01 (Table 2) ==="
python -m exp.exp3

echo ""
echo "=== Experiment 4: Monte Carlo comparison, gamma=0.5 (Table 3) ==="
python -m exp.exp4

echo ""
echo "=== All experiments complete. Results are in results/ ==="
