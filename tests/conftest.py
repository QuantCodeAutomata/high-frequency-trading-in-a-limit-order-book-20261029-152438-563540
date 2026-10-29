"""
Pytest configuration and shared fixtures for Avellaneda-Stoikov tests.
"""

import numpy as np
import pandas as pd
import pytest

from src.simulator import AvellanedaStoikovSimulator
from src import config


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "market_data: tests requiring live market-data API credentials (skipped by default)",
    )


@pytest.fixture(scope="session")
def default_params():
    """Return the paper's default simulation parameters."""
    return dict(
        s0=config.S0,
        T=config.T,
        sigma=config.SIGMA,
        dt=config.DT,
        gamma=config.GAMMA_EXP2,
        k=config.K,
        A=config.A,
        q0=config.Q0,
        x0=config.X0,
    )


@pytest.fixture(scope="session")
def sim_gamma01(default_params):
    """Simulator with gamma=0.1 (paper base case)."""
    return AvellanedaStoikovSimulator(**default_params)


@pytest.fixture(scope="session")
def rng_fixture():
    """Deterministic RNG for tests."""
    return np.random.default_rng(0)


@pytest.fixture(scope="session")
def single_path_gamma01(sim_gamma01):
    """One simulated path for gamma=0.1; session-scoped to avoid repeated simulation."""
    rng = np.random.default_rng(1)
    return sim_gamma01.simulate_single_path(rng, strategy="inventory")


@pytest.fixture(scope="session")
def mc_small(default_params):
    """Small Monte Carlo run (50 paths) for fast unit tests."""
    sim = AvellanedaStoikovSimulator(**default_params)
    rng = np.random.default_rng(7)
    return sim.run_monte_carlo(n_paths=50, rng=rng)
