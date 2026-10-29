"""
Configuration for all Avellaneda-Stoikov experiments.

Parameters are taken from Section 3.3 of Avellaneda & Stoikov (2008).
All module-level variables; no classes or parameter dicts.
"""

# ---------------------------------------------------------------------------
# Base simulation parameters (Section 3.3, page 10)
# ---------------------------------------------------------------------------

S0 = 100.0
# Initial mid-price; not specified in the paper (100 used in simulation)

T = 1.0
# Trading horizon; unit: normalized time; source: Section 3.3

SIGMA = 2.0
# Mid-price volatility coefficient in dS = sigma*dW; source: Section 3.3

DT = 0.005
# Simulation time step; source: Section 3.3

Q0 = 0
# Initial inventory; source: Section 3.3

X0 = 0.0
# Initial cash wealth; the paper does not specify X0; set to 0 so that
# terminal P&L = X_T + q_T*S_T equals trading profit from zero initial wealth.

# ---------------------------------------------------------------------------
# Order-arrival parameters (eq 3.8)
# ---------------------------------------------------------------------------

K = 1.5
# Exponential decay rate of order arrival intensity; source: Section 3.3

A = 140.0
# Base order arrival intensity; source: Section 3.3

# ---------------------------------------------------------------------------
# Risk-aversion values (one per experiment)
# ---------------------------------------------------------------------------

GAMMA_EXP2 = 0.1
# Risk aversion for exp 2 (Table 1); source: Section 3.3

GAMMA_EXP3 = 0.01
# Risk aversion for exp 3 (Table 2); source: Section 3.3

GAMMA_EXP4 = 0.5
# Risk aversion for exp 4 (Table 3); source: Section 3.3

GAMMA_VALUES = [GAMMA_EXP2, GAMMA_EXP3, GAMMA_EXP4]
# All tested risk-aversion values; source: Section 3.3

# ---------------------------------------------------------------------------
# Monte Carlo parameters
# ---------------------------------------------------------------------------

N_PATHS = 1000
# Number of simulation paths; source: Section 3.3 ("1000 simulations")

MC_SEED = 42
# Random seed for reproducibility; not specified in the paper

# ---------------------------------------------------------------------------
# Exp 1 – single-path parameters (Section 3.3, Figure 1)
# ---------------------------------------------------------------------------

GAMMA_EXP1 = 0.1
# Risk aversion for the single-path illustration; source: Section 3.3

EXP1_SEED = 0
# Random seed for exp 1 single path; not specified in the paper

# ---------------------------------------------------------------------------
# Derived quantities (for reference / validation)
# ---------------------------------------------------------------------------

N_STEPS = int(round(T / DT))
# Number of time steps per path: T / dt = 200
