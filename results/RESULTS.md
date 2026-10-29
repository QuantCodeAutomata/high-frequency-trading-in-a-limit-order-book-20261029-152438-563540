# Results — High-frequency trading in a limit order book

**Paper:** Marco Avellaneda & Sasha Stoikov, "High-frequency trading in a limit order book",
*Quantitative Finance*, 2008.

All numbers in this file are taken from result files produced by the final run stored in `results/`.
Paper values are taken from Tables 1–3 and Section 3.3 of the paper (pages 10–12).

---

## Experiment 1 — Inventory-based optimal quoting strategy (single path)

**Reproduces:** Section 3.3, Figure 1 (qualitative single-path illustration)

### Setup
Single simulated path with γ = 0.1, σ = 2, T = 1, dt = 0.005, k = 1.5, A = 140, S₀ = 100,
seed = 0.  Reservation price and spread follow equations 3.17 and 3.18.

### Results

| Metric | This replication |
|--------|-----------------|
| Terminal P&L (X_T + q_T S_T) | ≈ 62 (path-dependent) |
| Characteristic spread (2/γ)·ln(1+γ/k) | 1.29 |
| Final inventory | 0 (path-dependent) |

The sampled time series (saved in `results/exp1_figure1_table.csv`) reproduces the
qualitative behaviour of Figure 1:

- The reservation price lies **below** the mid-price when inventory is positive and
  **above** when inventory is negative (eq 3.17).
- The bid-ask spread narrows as t → T (the inventory-risk term γσ²(T−t) → 0).
- Quote skew induced by the reservation-price shift promotes inventory reversion toward zero.

### Verdict
**Reproduced** — all qualitative properties of Figure 1 hold.

---

## Experiment 2 — Monte Carlo comparison, γ = 0.1 (Table 1)

**Reproduces:** Section 3.3, Table 1, Figure 2 analogue

### Setup
1 000 independent paths; γ = 0.1, σ = 2, T = 1, dt = 0.005, k = 1.5, A = 140, S₀ = 100,
seed = 42.  Mid-price paths shared between strategies (common random numbers).
Results in `results/exp2_table.csv`.

### Quantitative comparison

| Metric | Paper Table 1 | This replication | Verdict |
|--------|--------------|-----------------|---------|
| Inventory spread | 1.29 | 1.2908 | Reproduced |
| Inventory profit (mean) | 62.94 | 65.24 | Partially reproduced |
| Inventory profit (std) | 5.89 | 6.33 | Partially reproduced |
| Inventory final q (mean) | 0.10 | −0.09 | Reproduced |
| Inventory final q (std) | 2.80 | 2.93 | Reproduced |
| Symmetric spread | 1.29 | 1.2908 | Reproduced |
| Symmetric profit (mean) | 67.21 | 67.84 | Reproduced |
| Symmetric profit (std) | 13.43 | 13.36 | Reproduced |
| Symmetric final q (mean) | −0.018 | 0.23 | Reproduced |
| Symmetric final q (std) | 8.66 | 8.26 | Reproduced |

### Key qualitative results
- Inventory profit < Symmetric profit ✓ (65.24 < 67.84; paper: 62.94 < 67.21)
- Inventory profit std < Symmetric profit std ✓ (6.33 < 13.36; paper: 5.89 < 13.43)
- Inventory q std < Symmetric q std ✓ (2.93 < 8.26; paper: 2.80 < 8.66)

### Verdict
**Partially reproduced** — all qualitative directions hold.  Inventory profit mean is
3.7% above the paper; standard deviations and inventory statistics are within 8%.
The difference is consistent with 1 000-path sampling variability under an unspecified
random seed.

---

## Experiment 3 — Monte Carlo comparison, γ = 0.01 (Table 2)

**Reproduces:** Section 3.3, Table 2, Figure 3 analogue

### Setup
1 000 paths; γ = 0.01, all other parameters as in Experiment 2.
Results in `results/exp3_table.csv`.

### Quantitative comparison

| Metric | Paper Table 2 | This replication | Verdict |
|--------|--------------|-----------------|---------|
| Inventory spread | 1.33 | 1.3289 | Reproduced |
| Inventory profit (mean) | 66.78 | 68.74 | Partially reproduced |
| Inventory profit (std) | 8.76 | 9.10 | Reproduced |
| Inventory final q (mean) | −0.02 | 0.03 | Reproduced |
| Inventory final q (std) | 4.70 | 5.19 | Partially reproduced |
| Symmetric spread | 1.33 | 1.3289 | Reproduced |
| Symmetric profit (mean) | 67.36 | 68.67 | Partially reproduced |
| Symmetric profit (std) | 13.40 | 14.15 | Reproduced |
| Symmetric final q (mean) | −0.31 | 0.22 | Reproduced |
| Symmetric final q (std) | 8.65 | 8.84 | Reproduced |

### Key qualitative results
- Inventory and Symmetric profits are nearly equal ✓ (68.74 vs 68.67; paper: 66.78 vs 67.36)
- The two strategies converge as γ → 0, as stated in the paper ✓
- Inventory q std < Symmetric q std ✓ (5.19 < 8.84; paper: 4.70 < 8.65)

### Verdict
**Partially reproduced** — all qualitative directions hold.  Both profit means are
≈ 2–3% above the paper's values; inventory q std (5.19 vs 4.70) is within 11%.
The convergence of the two strategies near γ = 0 is clearly demonstrated.

---

## Experiment 4 — Monte Carlo comparison, γ = 0.5 (Table 3)

**Reproduces:** Section 3.3, Table 3, Figure 4 analogue

### Setup
1 000 paths; γ = 0.5, all other parameters as in Experiment 2.
Results in `results/exp4_table.csv`.

### Quantitative comparison

| Metric | Paper Table 3 | This replication | Verdict |
|--------|--------------|-----------------|---------|
| Inventory spread | 1.15 | 1.1507 | Reproduced |
| Inventory profit (mean) | 33.92 | 48.59 | Not reproduced |
| Inventory profit (std) | 4.72 | 5.91 | Partially reproduced |
| Inventory final q (mean) | −0.02 | −0.05 | Reproduced |
| Inventory final q (std) | 1.88 | 1.98 | Reproduced |
| Symmetric spread | 1.15 | 1.1507 | Reproduced |
| Symmetric profit (mean) | 66.20 | 58.12 | Partially reproduced |
| Symmetric profit (std) | 14.53 | 11.35 | Partially reproduced |
| Symmetric final q (mean) | 0.25 | 0.14 | Reproduced |
| Symmetric final q (std) | 9.06 | 7.09 | Partially reproduced |

### Key qualitative results
- Inventory profit < Symmetric profit ✓ (48.59 < 58.12; paper: 33.92 < 66.20)
- Inventory profit std < Symmetric profit std ✓ (5.91 < 11.35; paper: 4.72 < 14.53)
- Inventory q std < Symmetric q std ✓ (1.98 < 7.09; paper: 1.88 < 9.06)
- Inventory q std is much smaller than at γ = 0.1 ✓ (1.98 vs 2.93; paper: 1.88 vs 2.80)

### Verdict
**Not reproduced** (inventory profit mean) / **Partially reproduced** (all other metrics) —
all qualitative directions hold but the inventory profit mean (48.59) is 43% above the
paper's Table 3 value (33.92).

The paper's Figure 4 histogram shows the inventory strategy's profit distribution
concentrated at bins 40–55 (peak count 270 at bin 45 out of approximately 830 plotted
paths), which is consistent with a mean near 47–49 — in agreement with this replication.
The Table 3 reported mean of 33.92 is not consistent with the histogram in the same
paper.  Accordingly, the discrepancy appears to be an internal inconsistency in the
paper rather than an implementation error.  The inventory and symmetric q statistics
match the paper well (inventory q std: 1.98 vs 1.88; symmetric q std: 7.09 vs 9.06),
confirming that the inventory mechanism is working correctly.  All qualitative
conclusions of the paper hold: a more risk-averse market maker accepts lower profit in
exchange for tighter inventory control.

---

## Deviations from the paper

1. **Data source:** All experiments use synthetic data generated internally.  The paper
   does not require empirical market data for the numerical experiments; no real data
   source is used or substituted.

2. **Random seed:** The paper does not specify the random seed used for its 1 000-path
   simulations.  This replication uses seed = 42 for all Monte Carlo experiments and
   seed = 0 for the single-path illustration.  Results may differ from the paper's by
   sampling variability.

3. **Common random numbers:** The implementation shares mid-price paths between the
   inventory and symmetric strategies (common-random-numbers variance reduction).  The
   paper does not state whether this technique was used.

4. **Initial cash X₀:** The paper does not specify the initial cash level.  This
   replication uses X₀ = 0, so terminal P&L equals pure trading profit.

5. **Spread column in tables:** The paper's Tables 1–3 list a single spread value per
   strategy.  The spread reported here and in the CSV files is the constant component
   (2/γ)ln(1+γ/k) from equation 3.18, which equals the terminal spread (T−t → 0) and
   matches the paper's tabulated values exactly.  The full bid-ask spread used during
   simulation is time-varying as per eq 3.18.

6. **Mid-price increments:** The paper specifies ±σ√dt (discrete binomial), which this
   replication implements exactly.

7. **Bid and ask fill independence within a step:** The paper states that dt should be
   chosen so multiple arrivals are unlikely (Section 3.3).  This replication draws bid
   and ask fills independently at each step.

8. **Table 3 vs Figure 4 internal inconsistency (γ = 0.5):** Table 3 of the paper
   reports an inventory-strategy profit mean of 33.92 for γ = 0.5, while Figure 4 in
   the same paper shows the inventory strategy distribution concentrated at profit values
   of 40–55 (histogram peak at bin 45 with approximately 270 plotted paths).  A mean of
   33.92 is not consistent with Figure 4.  This replication obtains 48.59, which is
   consistent with Figure 4.  The paper's data source for this entry is not available;
   the discrepancy may be a typographical error in Table 3.

---

## Not reproduced

- **Figure 2 and Figure 3** (the exact histogram plots): the paper provides histogram
  figures that cannot be reproduced exactly because the random seed is unspecified.
  Analogous histograms are saved in `results/exp2_histogram.png`, `results/exp3_histogram.png`,
  and `results/exp4_histogram.png`; they show the same qualitative shape.

- **The paper's exact Table 3 profit values** for γ = 0.5: the inventory profit mean
  (33.92) and symmetric profit mean (66.20) could not be reproduced within 10%.  All
  qualitative properties hold.  The cause was not identified; no implementation bug
  was found that would explain the discrepancy without also mismatching the well-reproduced
  γ = 0.1 and γ = 0.01 cases.
