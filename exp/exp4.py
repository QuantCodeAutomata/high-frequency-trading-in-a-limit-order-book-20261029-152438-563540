"""
Experiment 4: Monte Carlo comparison at gamma = 0.5 (Table 3).

Reproduces Table 3 of Avellaneda & Stoikov (2008):
  1000 simulations with gamma = 0.5.

A highly risk-averse market maker; the paper states that strong inventory
aversion reduces both P&L and P&L variance, and sharply lowers terminal
inventory dispersion.

Saves:
  results/exp4_table.csv      – summary statistics for both strategies
  results/exp4_histogram.png  – overlaid profit histograms (Figure 4 analogue)
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data.generate_synthetic import generate_monte_carlo
from src import config

RESULTS_DIR = "results"


def run_exp4(
    gamma: float = config.GAMMA_EXP4,
    n_paths: int = config.N_PATHS,
    seed: int = config.MC_SEED,
) -> pd.DataFrame:
    """Run Monte Carlo comparison for gamma = 0.5 and save results."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    print(f"Exp 4 – Monte Carlo comparison, gamma={gamma}, n_paths={n_paths}")

    mc = generate_monte_carlo(gamma=gamma, n_paths=n_paths, seed=seed)
    stats = _compute_and_save(mc, gamma, n_paths, tag="exp4", table_label="Table 3")
    return stats


def _compute_and_save(
    mc: dict, gamma: float, n_paths: int, tag: str, table_label: str
) -> pd.DataFrame:
    """Compute summary statistics, save CSV and histogram."""
    inv = mc["inventory"]
    sym = mc["symmetric"]

    rows = []
    for label, data in [("Inventory", inv), ("Symmetric", sym)]:
        rows.append({
            "Strategy": label,
            "Spread": round(data["spread"], 4),
            "Profit (mean)": round(float(np.mean(data["profits"])), 4),
            "Profit (std)": round(float(np.std(data["profits"], ddof=1)), 4),
            "Final q (mean)": round(float(np.mean(data["final_q"])), 4),
            "Final q (std)": round(float(np.std(data["final_q"], ddof=1)), 4),
        })

    stats = pd.DataFrame(rows)
    csv_path = os.path.join(RESULTS_DIR, f"{tag}_table.csv")
    stats.to_csv(csv_path, index=False)

    print(f"\n  {table_label}: 1000 simulations with gamma = {gamma}")
    print(stats.to_string(index=False))

    # ------------------------------------------------------------------
    # Profit histogram – inventory strategy should be tightly concentrated
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    bins = np.arange(-20, 160, 5)
    ax.hist(inv["profits"], bins=bins, alpha=0.6, color="blue",
            label="Inventory strategy", density=False)
    ax.hist(sym["profits"], bins=bins, alpha=0.6, color="red",
            label="Symmetric strategy", density=False)
    ax.set_xlabel("Profit (X_T + q_T * S_T)")
    ax.set_ylabel("Count")
    ax.set_title(f"P&L histogram – gamma = {gamma} ({n_paths} paths)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig_path = os.path.join(RESULTS_DIR, f"{tag}_histogram.png")
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"\n  Saved: {csv_path}, {fig_path}")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exp 4: Monte Carlo comparison, gamma=0.5 (Table 3)"
    )
    parser.add_argument("--gamma", type=float, default=config.GAMMA_EXP4)
    parser.add_argument("--n_paths", type=int, default=config.N_PATHS)
    parser.add_argument("--seed", type=int, default=config.MC_SEED)
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    run_exp4(gamma=args.gamma, n_paths=args.n_paths, seed=args.seed)


if __name__ == "__main__":
    main()
