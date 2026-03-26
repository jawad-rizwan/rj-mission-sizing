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
| TSFC | 0.5167 cruise / 0.4134 loiter [lb/(lb·hr)] |
| Cruise | Mach 0.78 at 35,000 ft |
| Wing Area | 1,016.58 ft² |
| Aspect Ratio | 7.8 |
| Oswald e | 0.727 |
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

*Fixed W0 = 65,000 lbs, same airframe as ZRJ70 (We = 50,136 lbs). Mission is infeasible — see below.

Composite factor of 0.97 reflects composite wing + tail with metal fuselage.

## Results

| Parameter | ZRJ70 (Comp) | ZRJ100 (Comp) | ZRJ70 (No Comp) | ZRJ100 (No Comp) |
|-----------|-------------|---------------|-----------------|-------------------|
| W0 [lbs] | 90,711 | 94,611 | 94,614 | 98,311 |
| We [lbs] | 50,136 | 51,640 | 53,238 | 54,690 |
| Total Fuel [lbs] | 21,732 | 18,803 | 22,532 | 19,453 |
| Trip Fuel [lbs] | 17,025 | 13,905 | 17,631 | 14,371 |
| Reserve Fuel [lbs] | 4,707 | 4,897 | 4,901 | 5,081 |
| T/W (SLS) | 0.423 | 0.406 | 0.406 | 0.390 |
| W/S [psf] | 89.2 | 93.1 | 93.1 | 96.7 |
| L/D cruise | 14.83 | 14.67 | 15.01 | 14.82 |
| (L/D)_max | 15.55 | 15.27 | 15.55 | 15.27 |
| Growth Factor | 5.02 | 4.05 | 5.24 | 4.20 |

### ZRJ50 (Composite) — Same Airframe, Fixed W0 = 65,000 lbs

CRJ550-style derivative: same airframe as ZRJ70 (We = 50,136 lbs), reconfigured to 50-seat cabin, constrained to W0 = 65,000 lbs.

**Result: Infeasible at 65,000 lbs.** Even at zero cruise range, overhead weight (We + min fuel + crew + payload = 69,874 lbs) exceeds the cap by 4,874 lbs. The minimum W0 for any useful mission is ~70,461 lbs.

W0 vs. maximum range (same airframe, same payload):

| W0 [lbs] | Max Range [nm] |
|-----------|---------------|
| 70,000 | Infeasible |
| 72,000 | 324 |
| 74,000 | 614 |
| 76,000 | 903 |
| 78,000 | 1,189 |
| 80,000 | 1,473 |
| 82,000 | 1,753 |
| 84,000 | 2,030 |

## Methods

- **Fuel fractions**: Warmup/takeoff (Eq 6.8), climb (Eq 6.9), cruise Breguet (Eq 6.11), loiter Breguet (Eq 6.14), landing (Eq 6.22/6.23)
- **Empty weight**: Refined regression from Table 6.1 (jet transport) with composite factor
- **Mission profile**: FAR 121.645 international — cruise, contingency loiter, attempted landing, go-around, divert to alternate (100 nm), regulatory hold (30 min), land
- **Iteration**: Damped fixed-point iteration on W0 with drag-polar L/D update each step
