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
| `plots.py` | Matplotlib visualizations — weight breakdown, range sensitivity, fuel burn profile, variant comparison |
| `plots_output/` | Generated chart images |

## Design Parameters

| Parameter | Value |
|-----------|-------|
| Engine | PW1200G (2 × 19,190 lbf SLS, BPR 9) |
| TSFC | 0.46 cruise / 0.37 loiter [lb/(lb·hr)] |
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

*Fixed W0 = 65,000 lbs, same airframe as ZRJ70 (We = 48,704 lbs). Mission is infeasible — see below.

Composite factor of 0.97 reflects composite wing + tail with metal fuselage.

## Results

| Parameter | ZRJ70 (Comp) | ZRJ100 (Comp) | ZRJ70 (No Comp) | ZRJ100 (No Comp) |
|-----------|-------------|---------------|-----------------|-------------------|
| W0 [lbs] | 87,043 | 91,927 | 90,710 | 95,473 |
| We [lbs] | 48,704 | 50,607 | 51,687 | 53,577 |
| Total Fuel [lbs] | 19,495 | 17,152 | 20,180 | 17,728 |
| Trip Fuel [lbs] | 15,168 | 12,604 | 15,679 | 13,012 |
| Reserve Fuel [lbs] | 4,327 | 4,548 | 4,501 | 4,715 |
| T/W (SLS) | 0.441 | 0.418 | 0.423 | 0.402 |
| W/S [psf] | 85.6 | 90.4 | 89.2 | 93.9 |
| L/D cruise | 14.81 | 14.73 | 15.01 | 14.90 |
| (L/D)_max | 15.82 | 15.54 | 15.82 | 15.54 |
| Growth Factor | 4.82 | 3.93 | 5.02 | 4.08 |

### ZRJ50 (Composite) — Same Airframe, Fixed W0 = 65,000 lbs

CRJ550-style derivative: same airframe as ZRJ70 (We = 48,704 lbs), reconfigured to 50-seat cabin, constrained to W0 = 65,000 lbs.

**Result: Infeasible at 65,000 lbs.** Even at zero cruise range, overhead weight (We + min fuel + crew + payload = 68,210 lbs) exceeds the cap by 3,210 lbs. The minimum W0 for any useful mission is ~68,586 lbs.

W0 vs. maximum range (same airframe, same payload):

| W0 [lbs] | Max Range [nm] |
|-----------|---------------|
| 65,000 | Infeasible |
| 68,000 | Infeasible |
| 70,000 | 337 |
| 72,000 | 671 |
| 74,000 | 1,004 |
| 76,000 | 1,334 |
| 78,000 | 1,662 |
| 80,000 | 1,987 |

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate (100 nm), regulatory hold (30 min), land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
