"""
Experiment 1: Single-path visualisation of the inventory-based quoting strategy.

Reproduces the qualitative behaviour of Figure 1 in Avellaneda & Stoikov (2008):
  - Reservation price shifts below mid-price when inventory is positive and
    above when inventory is negative.
  - Bid-ask spread narrows as t approaches T.
  - Quote skew induces inventory mean-reversion toward zero.

Saves:
  results/exp1_path.csv       – full time-series of one simulated path
  results/exp1_figure1.png    – mid-price, reservation price, bid, ask quotes
  results/exp1_figure1_table.csv – sampled at the time points shown in Figure 1
"""

import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data.generate_synthetic import generate_single_path
from src import config
from src.simulator import characteristic_spread

RESULTS_DIR = "results"


def _sample_at_times(df: pd.DataFrame, times: list) -> pd.DataFrame:
    """Return rows closest to the requested times."""
    rows = []
    for t in times:
        idx = (df["time"] - t).abs().idxmin()
        rows.append(df.loc[idx])
    return pd.DataFrame(rows).reset_index(drop=True)


def run_exp1(gamma: float = config.GAMMA_EXP1, seed: int = config.EXP1_SEED) -> None:
    """Run single-path simulation and produce Figure 1 artefacts."""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Exp 1 – single path, gamma={gamma}, seed={seed}")
    path = generate_single_path(gamma=gamma, seed=seed, strategy="inventory")

    profit = path.attrs["profit"]
    final_q = path.attrs["final_q"]
    spread = characteristic_spread(gamma, config.K)

    print(f"  Terminal P&L : {profit:.4f}")
    print(f"  Final inventory : {final_q:.0f}")
    print(f"  Characteristic spread : {spread:.4f}")

    # ------------------------------------------------------------------
    # Save full path CSV
    # ------------------------------------------------------------------
    path.to_csv(os.path.join(RESULTS_DIR, "exp1_path.csv"), index=False)

    # ------------------------------------------------------------------
    # Figure-1-style table at coarse time points
    # ------------------------------------------------------------------
    fig1_times = [0.0, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    sampled = _sample_at_times(path, fig1_times)
    display_cols = ["time", "mid_price", "ask_quote", "bid_quote", "res_price"]
    sampled[display_cols].round(1).to_csv(
        os.path.join(RESULTS_DIR, "exp1_figure1_table.csv"), index=False
    )
    print("\n  Figure-1 style table (sampled):")
    print(sampled[display_cols].round(2).to_string(index=False))

    # ------------------------------------------------------------------
    # Plot: mid-price, reservation price, bid/ask quotes vs time
    # ------------------------------------------------------------------
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax = axes[0]
    ax.plot(path["time"], path["mid_price"], color="black", lw=1.5,
            label="Mid-price")
    ax.plot(path["time"], path["res_price"], color="blue", lw=1.5,
            linestyle="--", label="Reservation price")
    ax.plot(path["time"], path["ask_quote"], color="red", lw=1.0,
            linestyle=":", label="Ask quote")
    ax.plot(path["time"], path["bid_quote"], color="green", lw=1.0,
            linestyle=":", label="Bid quote")
    ax.set_ylabel("Price")
    ax.legend(fontsize=8)
    ax.set_title(
        f"Avellaneda-Stoikov inventory strategy – single path "
        f"(γ={gamma}, σ={config.SIGMA}, T={config.T})"
    )
    ax.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.step(path["time"], path["inventory"], where="post", color="purple", lw=1.2)
    ax2.axhline(0, color="black", lw=0.8, linestyle="--")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Inventory")
    ax2.set_title("Inventory over time")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig_path = os.path.join(RESULTS_DIR, "exp1_figure1.png")
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"\n  Saved: {fig_path}")

    # ------------------------------------------------------------------
    # Qualitative checks (exclude terminal step where T-t=0 so r=s)
    # ------------------------------------------------------------------
    inner = path[path["time"] < config.T - config.DT / 2]
    pos_inv = inner[inner["inventory"] > 0]
    neg_inv = inner[inner["inventory"] < 0]
    if len(pos_inv) > 0:
        assert (pos_inv["res_price"] < pos_inv["mid_price"]).all(), \
            "Reservation price should be below mid-price when inventory > 0"
    if len(neg_inv) > 0:
        assert (neg_inv["res_price"] > neg_inv["mid_price"]).all(), \
            "Reservation price should be above mid-price when inventory < 0"
    print("  Qualitative checks passed (reservation price sign vs inventory).")

    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exp 1: single-path Avellaneda-Stoikov simulation"
    )
    parser.add_argument("--gamma", type=float, default=config.GAMMA_EXP1)
    parser.add_argument("--seed", type=int, default=config.EXP1_SEED)
    args = parser.parse_args()
    run_exp1(gamma=args.gamma, seed=args.seed)


if __name__ == "__main__":
    main()
