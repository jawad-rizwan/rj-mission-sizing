# Regional Jet Mission Sizing

Iterative takeoff weight sizing tool based on Raymer's *Aircraft Design: A Conceptual Approach* (Chapter 6). Uses a fixed engine and refined empty weight regression (Table 6.1) with drag-polar-based L/D.

## Requirements

- Python 3.10+
- `matplotlib` (for plots only)

## Usage

```bash
# Run sizing for all variants
python3 main.py

# Generate plots
python3 plots.py
```

## Project Structure

| File / Dir | Description |
|------------|-------------|
| `sizing.py` | Core sizing solver — atmosphere model, Breguet equations, empty weight regression, iterative W0 solver |
| `configs.py` | Mission profile builder and aircraft variant assembly from data files |
| `data/` | Per-aircraft data files (`ZRJ70.py`, `ZRJ100.py`, `ZRJ50.py`) |
| `main.py` | CLI output — per-variant results, comparison table, range sensitivity |
| `plots.py` | Matplotlib visualizations — weight breakdown, range sensitivity, fuel burn profile, mission profile, variant comparison |
| `plots_output/` | Generated chart images |

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Engine | PW1200G (2 × 19,190 lbf SLS, BPR 9) |
| TSFC | 0.50 cruise / 0.40 loiter [lb/(lb·hr)] |
| Cruise | Mach 0.78 at 35,000 ft |
| Wing Area | 1,016.58 ft² |
| Aspect Ratio | 7.8 |
| Oswald e | 0.753 |
| Alternate Range | 100 nm |
| Regulatory Hold | 30 min |
| Contingency | 10% of cruise time |

## Variants

| Variant | Pax | Payload (lbs) | Range (nm) | CD0 | Composite |
|---------|-----|--------------|------------|-----|-----------|
| ZRJ70 (Composite) | 76 | 18,055 | 1,800 | 0.01843 | 0.97 |
| ZRJ100 (Composite) | 100 | 23,380 | 1,200 | 0.01910 | 0.97 |
| ZRJ70 (No Composite) | 76 | 18,055 | 1,800 | 0.01843 | 1.00 |
| ZRJ100 (No Composite) | 100 | 23,380 | 1,200 | 0.01910 | 1.00 |
| ZRJ50 (Composite) | 50 | 11,350 | 1,800* | 0.01843 | 0.97 |

*Fixed W0 = 65,000 lbs, same airframe as ZRJ70 (We = 49,600 lbs). Mission is infeasible — see below.

Composite factor of 0.97 reflects composite wing + tail with metal fuselage.

## Results

| Parameter | ZRJ70 (Comp) | ZRJ100 (Comp) | ZRJ70 (No Comp) | ZRJ100 (No Comp) |
|-----------|-------------|---------------|-----------------|-------------------|
| W0 [lbs] | 89,332 | 93,598 | 93,133 | 97,231 |
| We [lbs] | 49,600 | 51,251 | 52,652 | 54,268 |
| Total Fuel [lbs] | 20,889 | 18,179 | 21,638 | 18,795 |
| Trip Fuel [lbs] | 16,329 | 13,417 | 16,892 | 13,857 |
| Reserve Fuel [lbs] | 4,560 | 4,761 | 4,745 | 4,938 |
| T/W (SLS) | 0.430 | 0.410 | 0.412 | 0.395 |
| W/S [psf] | 87.9 | 92.1 | 91.6 | 95.6 |
| L/D cruise | 14.94 | 14.81 | 15.13 | 14.97 |
| (L/D)_max | 15.82 | 15.54 | 15.82 | 15.54 |
| Growth Factor | 4.95 | 4.00 | 5.16 | 4.16 |

### ZRJ50 (Composite) — Same Airframe, Fixed W0 = 65,000 lbs

CRJ550-style derivative: same airframe as ZRJ70 (We = 49,600 lbs), reconfigured to 50-seat cabin, constrained to W0 = 65,000 lbs.

**Result: Infeasible at 65,000 lbs.** Even at zero cruise range, overhead weight (We + min fuel + crew + payload = 69,252 lbs) exceeds the cap by 4,252 lbs. The minimum W0 for any useful mission is ~69,758 lbs.

W0 vs. maximum range (same airframe, same payload):

| W0 [lbs] | Max Range [nm] |
|-----------|---------------|
| 65,000 | Infeasible |
| 69,000 | Infeasible |
| 71,000 | 290 |
| 73,000 | 595 |
| 75,000 | 899 |
| 77,000 | 1,199 |
| 79,000 | 1,498 |
| 81,000 | 1,795 |

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate (100 nm), regulatory hold (30 min), land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
