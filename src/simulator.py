"""
Avellaneda-Stoikov market-making simulator.

Implements the approximate finite-horizon strategy from Section 3.2 of
Avellaneda & Stoikov (2008):
  - Reservation price (indifference price): equation 3.17
  - Bid-ask spread formula: equation 3.18
  - Symmetric exponential order-arrival intensity: equation 3.8
  - Simulation procedure: Section 3.3
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.random import Generator
from typing import Dict, Any, Tuple


def reservation_price(s: np.ndarray, q: np.ndarray, t: float,
                      gamma: float, sigma: float, T: float) -> np.ndarray:
    """
    Compute the reservation (indifference) price.

    From equation 3.17: r(s, q, t) = s - q * gamma * sigma^2 * (T - t).

    Parameters
    ----------
    s : array-like
        Current mid-price(s).
    q : array-like
        Current inventory position(s).
    t : float
        Current time.
    gamma : float
        Risk-aversion coefficient.
    sigma : float
        Mid-price volatility.
    T : float
        Terminal time.

    Returns
    -------
    np.ndarray
        Reservation price(s).
    """
    # Paper eq 3.17: r = s - q * gamma * sigma^2 * (T - t)
    return s - q * gamma * sigma ** 2 * (T - t)


def total_spread(t: float, gamma: float, sigma: float, T: float, k: float) -> float:
    """
    Compute the total bid-ask spread (delta^a + delta^b).

    From equation 3.18:
        delta^a + delta^b = gamma * sigma^2 * (T - t) + (2 / gamma) * ln(1 + gamma / k).

    The constant term (2/gamma)*ln(1+gamma/k) matches the "spread" values
    reported in Tables 1–3 of Avellaneda & Stoikov (2008).

    Parameters
    ----------
    t : float
        Current time.
    gamma : float
        Risk-aversion coefficient.
    sigma : float
        Mid-price volatility.
    T : float
        Terminal time.
    k : float
        Order-arrival decay rate.

    Returns
    -------
    float
        Total spread at time t.
    """
    # Paper eq 3.18
    inventory_risk_term = gamma * sigma ** 2 * (T - t)
    # Use log1p for numerical stability when gamma/k is small
    arrival_term = (2.0 / gamma) * np.log1p(gamma / k)
    return inventory_risk_term + arrival_term


def characteristic_spread(gamma: float, k: float) -> float:
    """
    Compute the constant component of the spread: (2/gamma) * ln(1 + gamma/k).

    This equals the spread in the limit t → T (where the inventory-risk term
    vanishes) and matches the spread values in Tables 1–3 of the paper.

    Parameters
    ----------
    gamma : float
        Risk-aversion coefficient.
    k : float
        Order-arrival decay rate.

    Returns
    -------
    float
        Characteristic spread.
    """
    # Paper eq 3.18, constant component
    return (2.0 / gamma) * np.log1p(gamma / k)


def execution_intensity(delta: np.ndarray, A: float, k: float) -> np.ndarray:
    """
    Compute Poisson execution intensity for exponential order arrivals.

    From equation 3.8: lambda(delta) = A * exp(-k * delta).

    Parameters
    ----------
    delta : array-like
        Quote distance(s) from the mid-price.
    A : float
        Base arrival intensity.
    k : float
        Decay rate.

    Returns
    -------
    np.ndarray
        Execution intensity at each delta.
    """
    # Paper eq 3.8: symmetric exponential arrival rates
    return A * np.exp(-k * np.asarray(delta, dtype=float))


class AvellanedaStoikovSimulator:
    """
    Simulator for the Avellaneda-Stoikov limit-order-book market-making model.

    Encapsulates the approximate finite-horizon strategy (Section 3.2) and the
    simulation procedure (Section 3.3).

    Parameters
    ----------
    s0 : float
        Initial mid-price.
    T : float
        Time horizon.
    sigma : float
        Mid-price volatility (arithmetic Brownian motion).
    dt : float
        Simulation time step.
    gamma : float
        Risk-aversion coefficient.
    k : float
        Order-arrival decay rate.
    A : float
        Base order-arrival intensity.
    q0 : int, optional
        Initial inventory (default 0).
    x0 : float, optional
        Initial cash (default 0).
    """

    def __init__(self, s0: float, T: float, sigma: float, dt: float,
                 gamma: float, k: float, A: float,
                 q0: int = 0, x0: float = 0.0) -> None:
        self.s0 = float(s0)
        self.T = float(T)
        self.sigma = float(sigma)
        self.dt = float(dt)
        self.gamma = float(gamma)
        self.k = float(k)
        self.A = float(A)
        self.q0 = int(q0)
        self.x0 = float(x0)
        self.n_steps = int(round(T / dt))

        # Sanity check: Poisson intensity at delta=0 must be << 1/dt
        max_lambda_dt = self.A * self.dt
        if max_lambda_dt > 0.5:
            import warnings
            warnings.warn(
                f"Max lambda*dt = {max_lambda_dt:.3f} at delta=0 is not small; "
                "Bernoulli approximation to Poisson may introduce bias.",
                stacklevel=2
            )

    def _half_spread(self, t: float) -> float:
        """Half of the total spread from equation 3.18."""
        return 0.5 * total_spread(t, self.gamma, self.sigma, self.T, self.k)

    def simulate_single_path(
        self, rng: Generator, strategy: str = "inventory"
    ) -> pd.DataFrame:
        """
        Simulate a single path and return a timestamped DataFrame.

        The simulation procedure follows Section 3.3:
          1. Compute quotes from current state (s_t, q_t, t).
          2. With probability lambda^a(delta^a)*dt, sell one share at p^a
             (inventory decreases by 1, cash increases by p^a).
          3. With probability lambda^b(delta^b)*dt, buy one share at p^b
             (inventory increases by 1, cash decreases by p^b).
          4. Update mid-price by ±sigma*sqrt(dt).
          Repeat until T.

        Parameters
        ----------
        rng : numpy.random.Generator
            Random number generator.
        strategy : str
            "inventory" – quotes centred around reservation price (eq 3.17/3.18);
            "symmetric" – quotes centred around the mid-price with the same spread.

        Returns
        -------
        pd.DataFrame
            Columns: time, mid_price, res_price, bid_quote, ask_quote,
                     delta_b, delta_a, inventory, cash.
        """
        if strategy not in ("inventory", "symmetric"):
            raise ValueError(f"Unknown strategy '{strategy}'; use 'inventory' or 'symmetric'.")

        records = []
        s = self.s0
        q = float(self.q0)
        x = self.x0

        sqrt_dt = np.sqrt(self.dt)

        for i in range(self.n_steps):
            t = i * self.dt
            tau = self.T - t
            h = self._half_spread(t)
            r = reservation_price(s, q, t, self.gamma, self.sigma, self.T)

            if strategy == "inventory":
                pb = r - h  # eq: centre spread around reservation price
                pa = r + h
            else:
                pb = s - h  # symmetric: centre spread around mid-price
                pa = s + h

            delta_b = s - pb  # bid distance from mid-price
            delta_a = pa - s  # ask distance from mid-price

            lambda_b = execution_intensity(delta_b, self.A, self.k)
            lambda_a = execution_intensity(delta_a, self.A, self.k)

            # Bernoulli approximation to Poisson (Section 3.3)
            prob_b = float(np.clip(lambda_b * self.dt, 0.0, 1.0))
            prob_a = float(np.clip(lambda_a * self.dt, 0.0, 1.0))

            records.append({
                "time": t,
                "mid_price": s,
                "res_price": r,
                "bid_quote": pb,
                "ask_quote": pa,
                "delta_b": delta_b,
                "delta_a": delta_a,
                "inventory": q,
                "cash": x,
            })

            # Ask fill: inventory decreases, cash increases by p^a = s + delta^a
            if rng.random() < prob_a:
                q -= 1.0
                x += pa

            # Bid fill: inventory increases, cash decreases by p^b = s - delta^b
            if rng.random() < prob_b:
                q += 1.0
                x -= pb

            # Mid-price update: ±sigma*sqrt(dt) (Section 3.3)
            s += self.sigma * sqrt_dt * (1.0 if rng.random() < 0.5 else -1.0)

        # Record terminal state
        t = self.n_steps * self.dt
        h = self._half_spread(t)
        r = reservation_price(s, q, t, self.gamma, self.sigma, self.T)
        records.append({
            "time": t,
            "mid_price": s,
            "res_price": r,
            "bid_quote": s - h if strategy == "symmetric" else r - h,
            "ask_quote": s + h if strategy == "symmetric" else r + h,
            "delta_b": h,
            "delta_a": h,
            "inventory": q,
            "cash": x,
        })

        df = pd.DataFrame(records)
        # Terminal P&L: X_T + q_T * S_T
        df.attrs["profit"] = x + q * s
        df.attrs["final_q"] = q
        return df

    def run_monte_carlo(
        self, n_paths: int, rng: Generator
    ) -> Dict[str, Any]:
        """
        Run a vectorised Monte Carlo for both inventory and symmetric strategies.

        Mid-price paths are shared between strategies (common-random-numbers
        variance reduction). Fill decisions are independent for each strategy.

        Parameters
        ----------
        n_paths : int
            Number of simulation paths.
        rng : numpy.random.Generator
            Random number generator.

        Returns
        -------
        dict with keys "inventory" and "symmetric", each containing:
            profits  : np.ndarray, shape (n_paths,)
            final_q  : np.ndarray, shape (n_paths,)
            spread   : float  (characteristic spread, matching paper tables)
        """
        n = n_paths
        m = self.n_steps
        sqrt_dt = np.sqrt(self.dt)

        # --- Pre-draw random numbers ------------------------------------------
        # Mid-price signs shared between strategies (common random numbers)
        signs = (rng.integers(0, 2, size=(n, m)) * 2 - 1).astype(float)
        # Fill decisions: (n_paths, n_steps) uniform draws, independent per side
        u_a_inv = rng.random(size=(n, m))   # ask fill, inventory strategy
        u_b_inv = rng.random(size=(n, m))   # bid fill, inventory strategy
        u_a_sym = rng.random(size=(n, m))   # ask fill, symmetric strategy
        u_b_sym = rng.random(size=(n, m))   # bid fill, symmetric strategy

        # --- State arrays -------------------------------------------------------
        s = np.full(n, self.s0)           # shared mid-price
        q_inv = np.full(n, float(self.q0))
        x_inv = np.full(n, self.x0)
        q_sym = np.full(n, float(self.q0))
        x_sym = np.full(n, self.x0)

        # --- Time loop ----------------------------------------------------------
        for step in range(m):
            t = step * self.dt

            h = self._half_spread(t)
            tau = self.T - t

            # --- Inventory strategy -------------------------------------------
            r = s - q_inv * self.gamma * self.sigma ** 2 * tau  # eq 3.17
            pb_inv = r - h
            pa_inv = r + h

            delta_b_inv = s - pb_inv          # = h + q_inv*gamma*sigma^2*tau
            delta_a_inv = pa_inv - s          # = h - q_inv*gamma*sigma^2*tau

            lam_a_inv = self.A * np.exp(-self.k * delta_a_inv)
            lam_b_inv = self.A * np.exp(-self.k * delta_b_inv)
            p_a_inv = np.clip(lam_a_inv * self.dt, 0.0, 1.0)
            p_b_inv = np.clip(lam_b_inv * self.dt, 0.0, 1.0)

            fa = u_a_inv[:, step] < p_a_inv   # ask fills
            fb = u_b_inv[:, step] < p_b_inv   # bid fills

            # Ask fill: sell at p^a (inventory - 1, cash + p^a)
            x_inv += fa * pa_inv
            q_inv -= fa.astype(float)
            # Bid fill: buy at p^b (inventory + 1, cash - p^b)
            x_inv -= fb * pb_inv
            q_inv += fb.astype(float)

            # --- Symmetric strategy -------------------------------------------
            pb_sym = s - h
            pa_sym = s + h
            # Both sides use the same delta = h
            p_sym = float(np.clip(self.A * np.exp(-self.k * h) * self.dt, 0.0, 1.0))

            fa_s = u_a_sym[:, step] < p_sym
            fb_s = u_b_sym[:, step] < p_sym

            x_sym += fa_s * pa_sym
            q_sym -= fa_s.astype(float)
            x_sym -= fb_s * pb_sym
            q_sym += fb_s.astype(float)

            # --- Mid-price update (shared) ------------------------------------
            s += signs[:, step] * self.sigma * sqrt_dt

        # Terminal P&L: X_T + q_T * S_T
        pnl_inv = x_inv + q_inv * s
        pnl_sym = x_sym + q_sym * s

        spread = characteristic_spread(self.gamma, self.k)

        return {
            "inventory": {
                "profits": pnl_inv,
                "final_q": q_inv,
                "spread": spread,
            },
            "symmetric": {
                "profits": pnl_sym,
                "final_q": q_sym,
                "spread": spread,
            },
        }
