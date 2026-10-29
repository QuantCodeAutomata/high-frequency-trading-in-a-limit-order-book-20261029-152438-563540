"""
Synthetic data generation for Avellaneda-Stoikov experiments.

All synthetic simulation data used by the experiments is produced here.
Calls src.simulator for the core model logic.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Any

from src.simulator import AvellanedaStoikovSimulator
from src import config


def _make_simulator(gamma: float) -> AvellanedaStoikovSimulator:
    """Construct a simulator with paper parameters and a given risk aversion."""
    return AvellanedaStoikovSimulator(
        s0=config.S0,
        T=config.T,
        sigma=config.SIGMA,
        dt=config.DT,
        gamma=gamma,
        k=config.K,
        A=config.A,
        q0=config.Q0,
        x0=config.X0,
    )


def generate_single_path(
    gamma: float = config.GAMMA_EXP1,
    seed: int = config.EXP1_SEED,
    strategy: str = "inventory",
) -> pd.DataFrame:
    """
    Simulate a single market-making path and return a time-series DataFrame.

    Used by exp1 to reproduce the qualitative behaviour shown in Figure 1
    of Avellaneda & Stoikov (2008).

    Parameters
    ----------
    gamma : float
        Risk-aversion coefficient.
    seed : int
        Random seed for reproducibility.
    strategy : str
        "inventory" or "symmetric".

    Returns
    -------
    pd.DataFrame
        Columns: time, mid_price, res_price, bid_quote, ask_quote,
                 delta_b, delta_a, inventory, cash.
        DataFrame.attrs contains "profit" and "final_q".
    """
    rng = np.random.default_rng(seed)
    sim = _make_simulator(gamma)
    return sim.simulate_single_path(rng, strategy=strategy)


def generate_monte_carlo(
    gamma: float,
    n_paths: int = config.N_PATHS,
    seed: int = config.MC_SEED,
) -> Dict[str, Any]:
    """
    Run a Monte Carlo comparison of the inventory and symmetric strategies.

    Shared mid-price paths are used for both strategies (common random numbers).
    Fill decisions are drawn independently for each strategy.

    Parameters
    ----------
    gamma : float
        Risk-aversion coefficient.
    n_paths : int
        Number of simulation paths.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    dict
        Keys "inventory" and "symmetric", each mapping to a dict with:
          profits  : np.ndarray, shape (n_paths,) – terminal P&L per path
          final_q  : np.ndarray, shape (n_paths,) – terminal inventory per path
          spread   : float – characteristic spread (2/gamma)*ln(1+gamma/k)
    """
    rng = np.random.default_rng(seed)
    sim = _make_simulator(gamma)
    return sim.run_monte_carlo(n_paths=n_paths, rng=rng)
