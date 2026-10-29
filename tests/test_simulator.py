"""
Unit tests for src/simulator.py.

Tests verify the paper's stated properties:
  - Reservation price sign vs inventory (Section 2.2)
  - Spread formula and characteristic spread (eq 3.18)
  - Execution intensity (eq 3.8)
  - Simulation temporal structure (no look-ahead)
  - Cash bookkeeping correctness
  - Qualitative P&L properties across strategies
"""

import numpy as np
import pandas as pd
import pytest

from src.simulator import (
    AvellanedaStoikovSimulator,
    characteristic_spread,
    execution_intensity,
    reservation_price,
    total_spread,
)
from src import config


# ---------------------------------------------------------------------------
# Formula-level tests
# ---------------------------------------------------------------------------

class TestReservationPrice:
    def test_zero_inventory(self):
        """r(s, 0, t) == s for all s, t."""
        s = np.array([100.0, 80.0, 120.0])
        q = np.zeros(3)
        r = reservation_price(s, q, t=0.3, gamma=0.1, sigma=2.0, T=1.0)
        np.testing.assert_allclose(r, s)

    def test_positive_inventory_below_mid(self):
        """When q > 0, reservation price < mid-price (eq 3.17)."""
        r = reservation_price(s=100.0, q=2.0, t=0.5, gamma=0.1, sigma=2.0, T=1.0)
        assert r < 100.0, "Reservation price must be below mid when long"

    def test_negative_inventory_above_mid(self):
        """When q < 0, reservation price > mid-price (eq 3.17)."""
        r = reservation_price(s=100.0, q=-2.0, t=0.5, gamma=0.1, sigma=2.0, T=1.0)
        assert r > 100.0, "Reservation price must be above mid when short"

    def test_terminal_equals_midprice(self):
        """At t = T, reservation price equals mid-price (T-t term vanishes)."""
        r = reservation_price(s=100.0, q=5.0, t=1.0, gamma=0.1, sigma=2.0, T=1.0)
        assert abs(r - 100.0) < 1e-10

    def test_linear_in_inventory(self):
        """r is linear in q: r(s, q, t) = s - q * gamma * sigma^2 * (T-t)."""
        s, gamma, sigma, T, t = 100.0, 0.1, 2.0, 1.0, 0.5
        tau = T - t
        for q in [0, 1, -1, 3, -5]:
            expected = s - q * gamma * sigma ** 2 * tau
            got = float(reservation_price(s, float(q), t, gamma, sigma, T))
            assert abs(got - expected) < 1e-10, f"Failed for q={q}"


class TestSpread:
    def test_characteristic_spread_gamma01(self):
        """(2/0.1)*ln(1+0.1/1.5) ≈ 1.29, matching Table 1."""
        sp = characteristic_spread(gamma=0.1, k=1.5)
        assert abs(sp - 1.29) < 0.01, f"Expected ≈1.29, got {sp:.4f}"

    def test_characteristic_spread_gamma001(self):
        """(2/0.01)*ln(1+0.01/1.5) ≈ 1.33, matching Table 2."""
        sp = characteristic_spread(gamma=0.01, k=1.5)
        assert abs(sp - 1.33) < 0.01, f"Expected ≈1.33, got {sp:.4f}"

    def test_characteristic_spread_gamma05(self):
        """(2/0.5)*ln(1+0.5/1.5) ≈ 1.15, matching Table 3."""
        sp = characteristic_spread(gamma=0.5, k=1.5)
        assert abs(sp - 1.15) < 0.01, f"Expected ≈1.15, got {sp:.4f}"

    def test_total_spread_decreases_with_time(self):
        """Total spread decreases as t → T (inventory risk term shrinks)."""
        gamma, sigma, T, k = 0.1, 2.0, 1.0, 1.5
        times = [0.0, 0.25, 0.5, 0.75, 1.0]
        spreads = [total_spread(t, gamma, sigma, T, k) for t in times]
        for i in range(len(spreads) - 1):
            assert spreads[i] >= spreads[i + 1], (
                f"Spread should be non-increasing: {spreads[i]:.4f} → {spreads[i+1]:.4f}"
            )

    def test_total_spread_at_terminal_equals_characteristic(self):
        """At t=T, total spread equals characteristic spread."""
        gamma, sigma, T, k = 0.1, 2.0, 1.0, 1.5
        ts = total_spread(T, gamma, sigma, T, k)
        cs = characteristic_spread(gamma, k)
        assert abs(ts - cs) < 1e-10


class TestExecutionIntensity:
    def test_delta_zero_gives_A(self):
        """lambda(0) = A."""
        lam = float(execution_intensity(np.array([0.0]), A=140.0, k=1.5))
        assert abs(lam - 140.0) < 1e-10

    def test_decreasing_in_delta(self):
        """lambda is decreasing in delta (larger distance → lower fill rate)."""
        deltas = np.array([0.0, 0.5, 1.0, 2.0])
        lams = execution_intensity(deltas, A=140.0, k=1.5)
        assert np.all(np.diff(lams) < 0), "Intensity must decrease with delta"

    def test_positive(self):
        """Intensity is always positive."""
        deltas = np.linspace(-2, 5, 50)
        lams = execution_intensity(deltas, A=140.0, k=1.5)
        assert np.all(lams > 0)


# ---------------------------------------------------------------------------
# Simulator-level tests
# ---------------------------------------------------------------------------

class TestSimulatorConstruction:
    def test_n_steps(self, default_params):
        """n_steps = T / dt = 200."""
        sim = AvellanedaStoikovSimulator(**default_params)
        assert sim.n_steps == 200

    def test_warns_large_lambda_dt(self, default_params):
        """Should warn when A*dt is large (Bernoulli approximation concern)."""
        import warnings
        # A=140, dt=0.005: A*dt=0.7 > 0.5 → should warn
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            AvellanedaStoikovSimulator(**default_params)
        # Warning should have been issued
        assert len(w) >= 1, "Expected a warning about large lambda*dt"


class TestSinglePath:
    def test_returns_dataframe(self, single_path_gamma01):
        df = single_path_gamma01
        assert isinstance(df, pd.DataFrame)

    def test_correct_columns(self, single_path_gamma01):
        expected = {"time", "mid_price", "res_price", "bid_quote", "ask_quote",
                    "delta_b", "delta_a", "inventory", "cash"}
        assert expected <= set(single_path_gamma01.columns)

    def test_time_length(self, single_path_gamma01):
        """Path has n_steps + 1 rows (includes t=0 and t=T)."""
        df = single_path_gamma01
        assert len(df) == config.N_STEPS + 1

    def test_time_starts_at_zero(self, single_path_gamma01):
        assert single_path_gamma01["time"].iloc[0] == pytest.approx(0.0)

    def test_time_ends_at_T(self, single_path_gamma01):
        assert single_path_gamma01["time"].iloc[-1] == pytest.approx(config.T, abs=1e-9)

    def test_initial_mid_price(self, single_path_gamma01):
        assert single_path_gamma01["mid_price"].iloc[0] == pytest.approx(config.S0)

    def test_initial_inventory(self, single_path_gamma01):
        assert single_path_gamma01["inventory"].iloc[0] == config.Q0

    def test_reservation_price_sign_positive_inventory(self, single_path_gamma01):
        """When inventory > 0, reservation price must be below mid-price (Section 2.2).
        Excludes the terminal step where T-t=0 makes r=s exactly by definition."""
        df = single_path_gamma01
        # Exclude terminal step: at t=T the inventory-risk term (T-t) vanishes so r=s
        inner = df[df["time"] < config.T - config.DT / 2]
        pos = inner[inner["inventory"] > 0]
        if len(pos) > 0:
            assert (pos["res_price"] < pos["mid_price"]).all(), (
                "Reservation price must be below mid when inventory > 0"
            )

    def test_reservation_price_sign_negative_inventory(self, single_path_gamma01):
        """When inventory < 0, reservation price must be above mid-price (Section 2.2).
        Excludes the terminal step where T-t=0 makes r=s exactly by definition."""
        df = single_path_gamma01
        # Exclude terminal step: at t=T the inventory-risk term (T-t) vanishes so r=s
        inner = df[df["time"] < config.T - config.DT / 2]
        neg = inner[inner["inventory"] < 0]
        if len(neg) > 0:
            assert (neg["res_price"] > neg["mid_price"]).all(), (
                "Reservation price must be above mid when inventory < 0"
            )

    def test_res_price_converges_to_mid_near_terminal(self, single_path_gamma01):
        """Near t=T, |r - s| → 0 (inventory risk term vanishes)."""
        df = single_path_gamma01
        near_terminal = df[df["time"] >= 0.95]
        gap = (near_terminal["res_price"] - near_terminal["mid_price"]).abs()
        # Gap should be small relative to early-time gap
        early = df[df["time"] <= 0.1]
        if len(early) > 1:
            early_gap = (early["res_price"] - early["mid_price"]).abs().mean()
            if early_gap > 0:
                assert gap.mean() <= early_gap + 1e-6, (
                    "Reservation-price gap should not grow near terminal time"
                )

    def test_no_lookahead(self, default_params):
        """Quotes at step i are computed from state at step i (not i+1)."""
        sim = AvellanedaStoikovSimulator(**default_params)
        rng = np.random.default_rng(99)
        df = sim.simulate_single_path(rng, strategy="inventory")
        # At t=0, inventory = 0 → reservation price = mid-price
        row0 = df.iloc[0]
        expected_r0 = row0["mid_price"]  # q=0 → r = s
        assert abs(row0["res_price"] - expected_r0) < 1e-10

    def test_inventory_strategy_quotes_centre_on_reservation(self, default_params):
        """For inventory strategy: mid(bid, ask) = reservation price."""
        sim = AvellanedaStoikovSimulator(**default_params)
        rng = np.random.default_rng(42)
        df = sim.simulate_single_path(rng, strategy="inventory")
        mid_quote = 0.5 * (df["bid_quote"] + df["ask_quote"])
        np.testing.assert_allclose(mid_quote.values, df["res_price"].values,
                                   atol=1e-10)

    def test_symmetric_strategy_quotes_centre_on_mid(self, default_params):
        """For symmetric strategy: mid(bid, ask) = mid_price."""
        sim = AvellanedaStoikovSimulator(**default_params)
        rng = np.random.default_rng(42)
        df = sim.simulate_single_path(rng, strategy="symmetric")
        mid_quote = 0.5 * (df["bid_quote"] + df["ask_quote"])
        np.testing.assert_allclose(mid_quote.values, df["mid_price"].values,
                                   atol=1e-10)

    def test_profit_attr_exists(self, single_path_gamma01):
        assert "profit" in single_path_gamma01.attrs
        assert "final_q" in single_path_gamma01.attrs

    def test_profit_equals_terminal_wealth(self, single_path_gamma01):
        """Profit = X_T + q_T * S_T."""
        df = single_path_gamma01
        last = df.iloc[-1]
        expected = last["cash"] + last["inventory"] * last["mid_price"]
        assert abs(df.attrs["profit"] - expected) < 1e-6


class TestMonteCarlo:
    def test_returns_both_strategies(self, mc_small):
        assert "inventory" in mc_small
        assert "symmetric" in mc_small

    def test_profit_shape(self, mc_small):
        assert mc_small["inventory"]["profits"].shape == (50,)
        assert mc_small["symmetric"]["profits"].shape == (50,)

    def test_spread_values_match_characteristic(self, mc_small):
        expected = characteristic_spread(config.GAMMA_EXP2, config.K)
        assert abs(mc_small["inventory"]["spread"] - expected) < 1e-10
        assert abs(mc_small["symmetric"]["spread"] - expected) < 1e-10

    def test_inventory_strategy_lower_profit_std_gamma01(self, default_params):
        """Inventory strategy has lower profit std than symmetric at gamma=0.1 (paper claim)."""
        sim = AvellanedaStoikovSimulator(**default_params)
        rng = np.random.default_rng(123)
        mc = sim.run_monte_carlo(n_paths=200, rng=rng)
        std_inv = np.std(mc["inventory"]["profits"], ddof=1)
        std_sym = np.std(mc["symmetric"]["profits"], ddof=1)
        assert std_inv < std_sym, (
            f"Inventory std ({std_inv:.2f}) should be < symmetric std ({std_sym:.2f})"
        )

    def test_inventory_strategy_lower_final_q_std_gamma01(self, default_params):
        """Inventory strategy has lower final-inventory std than symmetric at gamma=0.1."""
        sim = AvellanedaStoikovSimulator(**default_params)
        rng = np.random.default_rng(456)
        mc = sim.run_monte_carlo(n_paths=200, rng=rng)
        std_inv = np.std(mc["inventory"]["final_q"], ddof=1)
        std_sym = np.std(mc["symmetric"]["final_q"], ddof=1)
        assert std_inv < std_sym, (
            f"Inventory final-q std ({std_inv:.2f}) should be < symmetric ({std_sym:.2f})"
        )

    def test_spread_monotone_in_gamma(self):
        """Characteristic spread is non-monotone; verify specific ordering from paper tables."""
        # gamma=0.1 → ≈1.29, gamma=0.01 → ≈1.33, gamma=0.5 → ≈1.15
        sp_01 = characteristic_spread(0.1, 1.5)
        sp_001 = characteristic_spread(0.01, 1.5)
        sp_05 = characteristic_spread(0.5, 1.5)
        # 0.01 gives the highest spread (less risk aversion, more patient quoting)
        assert sp_001 > sp_01 > sp_05


class TestEdgeCases:
    def test_zero_gamma_limit_approaches_symmetric(self):
        """For very small gamma, inventory and symmetric strategies should be very close."""
        sim = AvellanedaStoikovSimulator(
            s0=100, T=1, sigma=2, dt=0.005,
            gamma=1e-4, k=1.5, A=140, q0=0, x0=0.0
        )
        rng = np.random.default_rng(0)
        mc = sim.run_monte_carlo(n_paths=100, rng=rng)
        # P&L distributions should be very similar
        diff_mean = abs(np.mean(mc["inventory"]["profits"]) -
                        np.mean(mc["symmetric"]["profits"]))
        assert diff_mean < 5.0, f"Mean P&L diff too large for small gamma: {diff_mean:.4f}"

    def test_high_gamma_lower_inventory_variance(self):
        """High gamma → inventory strategy tightly controls inventory."""
        sim_high = AvellanedaStoikovSimulator(
            s0=100, T=1, sigma=2, dt=0.005,
            gamma=0.5, k=1.5, A=140, q0=0, x0=0.0
        )
        sim_low = AvellanedaStoikovSimulator(
            s0=100, T=1, sigma=2, dt=0.005,
            gamma=0.1, k=1.5, A=140, q0=0, x0=0.0
        )
        rng_h = np.random.default_rng(11)
        rng_l = np.random.default_rng(11)
        mc_high = sim_high.run_monte_carlo(n_paths=100, rng=rng_h)
        mc_low = sim_low.run_monte_carlo(n_paths=100, rng=rng_l)
        std_high = np.std(mc_high["inventory"]["final_q"], ddof=1)
        std_low = np.std(mc_low["inventory"]["final_q"], ddof=1)
        assert std_high < std_low, (
            "Higher gamma should yield lower inventory std in inventory strategy"
        )
